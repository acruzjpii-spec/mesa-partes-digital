import csv
import io
import os
import re
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.algoritmos import validar_expediente
from app.auth import require_role
from app.database import get_db
from app.models import Area, Documento, EstadoTramite, Movimiento, Prioridad, Rol, Tramite
from app.schemas import SeguimientoResponse, TramiteResponse, TramiteUpdate

router = APIRouter(prefix="/api/tramites", tags=["Trámites"])
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
MAX_ADJUNTO = 5 * 1024 * 1024
EXTENSIONES_PERMITIDAS = {".pdf", ".png", ".jpg", ".jpeg", ".docx", ".txt"}


def generar_codigo() -> str:
    return f"EXP-{uuid.uuid4().hex[:8].upper()}"


def parse_prioridad(valor: str) -> Prioridad:
    try:
        return Prioridad(valor)
    except ValueError:
        return Prioridad.NORMAL


@router.post("/", response_model=TramiteResponse)
def crear_tramite(
    asunto: str = Form(...),
    remitente_nombre: str = Form(...),
    remitente_email: Optional[str] = Form(None),
    remitente_dni: Optional[str] = Form(None),
    tipo_documento: Optional[str] = Form(None),
    prioridad: str = Form("normal"),
    observaciones: Optional[str] = Form(None),
    archivos: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    _=Depends(require_role([Rol.ADMIN, Rol.OPERADOR])),
):
    try:
        asunto, remitente_nombre, remitente_dni = validar_expediente(asunto, remitente_nombre, remitente_dni or "")
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    # Revisar archivos antes de confirmar la creación del trámite.
    adjuntos = []
    for archivo in archivos:
        if not archivo.filename:
            continue
        nombre_original = archivo.filename.replace("\\", "/").split("/")[-1]
        extension = os.path.splitext(nombre_original)[1].lower()
        if extension not in EXTENSIONES_PERMITIDAS:
            raise HTTPException(status_code=422, detail="Tipo de archivo no permitido")
        contenido = archivo.file.read(MAX_ADJUNTO + 1)
        if len(contenido) > MAX_ADJUNTO:
            raise HTTPException(status_code=413, detail="Archivo supera el límite de 5 MB")
        safe_name = re.sub(r"[^a-zA-Z0-9._-]", "_", nombre_original)[:150]
        adjuntos.append((nombre_original, safe_name, archivo.content_type, contenido))

    codigo = generar_codigo()
    mesa = db.query(Area).filter(Area.nombre == "Mesa de Partes").first()
    tramite = Tramite(
        codigo_seguimiento=codigo,
        asunto=asunto,
        remitente_nombre=remitente_nombre,
        remitente_email=remitente_email or None,
        remitente_dni=remitente_dni or None,
        tipo_documento=tipo_documento or None,
        prioridad=parse_prioridad(prioridad),
        observaciones=observaciones or None,
        area_actual_id=mesa.id if mesa else None,
    )
    db.add(tramite)
    db.commit()
    db.refresh(tramite)

    db.add(Movimiento(tramite_id=tramite.id, area_destino_id=tramite.area_actual_id, accion="recepcion", comentario="Trámite registrado en mesa de partes"))

    for nombre_original, nombre_seguro, tipo, contenido in adjuntos:
        ruta = os.path.join(UPLOAD_DIR, f"{codigo}_{uuid.uuid4().hex[:6]}_{nombre_seguro}")
        with open(ruta, "wb") as archivo_destino:
            archivo_destino.write(contenido)
        db.add(Documento(tramite_id=tramite.id, nombre_archivo=nombre_original, tipo_archivo=tipo,
                         ruta_storage=ruta, tamano_bytes=len(contenido)))

    db.commit()
    db.refresh(tramite)
    return tramite


@router.get("/seguimiento/{codigo}", response_model=SeguimientoResponse)
def seguimiento_publico(codigo: str, db: Session = Depends(get_db)):
    tramite = db.query(Tramite).filter(Tramite.codigo_seguimiento == codigo.upper()).first()
    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite no encontrado")
    return {
        "codigo_seguimiento": tramite.codigo_seguimiento,
        "asunto": tramite.asunto,
        "estado": tramite.estado,
        "fecha_recepcion": tramite.fecha_recepcion,
        "area_actual": tramite.area_actual.nombre if tramite.area_actual else "Mesa de Partes",
        "movimientos": tramite.movimientos,
    }


@router.get("/", response_model=List[TramiteResponse])
def listar_tramites(
    estado: Optional[EstadoTramite] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _=Depends(require_role([Rol.ADMIN, Rol.OPERADOR])),
):
    query = db.query(Tramite)
    if estado:
        query = query.filter(Tramite.estado == estado)
    return query.order_by(Tramite.fecha_recepcion.desc()).offset(skip).limit(limit).all()


@router.get("/exportar/csv")
def exportar_csv(db: Session = Depends(get_db), _=Depends(require_role([Rol.ADMIN, Rol.OPERADOR]))):
    """Copia CSV para evidenciar manejo de archivos sin sustituir SQLite."""
    filas = db.query(Tramite).order_by(Tramite.codigo_seguimiento.asc()).all()
    salida = io.StringIO()
    writer = csv.writer(salida)
    writer.writerow(["codigo", "asunto", "remitente", "estado"])
    for t in filas:
        writer.writerow([t.codigo_seguimiento, t.asunto, t.remitente_nombre, t.estado.value])
    return Response(content="\ufeff" + salida.getvalue(), media_type="text/csv; charset=utf-8",
                    headers={"Content-Disposition": "attachment; filename=expedientes.csv"})


@router.get("/{tramite_id}", response_model=TramiteResponse)
def obtener_tramite(tramite_id: int, db: Session = Depends(get_db), _=Depends(require_role([Rol.ADMIN, Rol.OPERADOR]))):
    tramite = db.query(Tramite).filter(Tramite.id == tramite_id).first()
    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite no encontrado")
    return tramite


@router.put("/{tramite_id}", response_model=TramiteResponse)
def actualizar_tramite(tramite_id: int, update: TramiteUpdate, db: Session = Depends(get_db), current_user=Depends(require_role([Rol.ADMIN, Rol.OPERADOR]))):
    tramite = db.query(Tramite).filter(Tramite.id == tramite_id).first()
    if not tramite:
        raise HTTPException(status_code=404, detail="Trámite no encontrado")

    if update.estado:
        tramite.estado = update.estado
        if update.estado == EstadoTramite.ATENDIDO:
            from datetime import datetime
            tramite.fecha_resolucion = datetime.utcnow()

    if update.area_actual_id:
        area = db.query(Area).filter(Area.id == update.area_actual_id).first()
        if not area:
            raise HTTPException(status_code=404, detail="Área no encontrada")
        db.add(Movimiento(tramite_id=tramite.id, area_origen_id=tramite.area_actual_id, area_destino_id=area.id, usuario_id=current_user.id, accion="derivacion", comentario=f"Derivado a {area.nombre}"))
        tramite.area_actual_id = area.id

    if update.observaciones is not None:
        tramite.observaciones = update.observaciones

    db.commit()
    db.refresh(tramite)
    return tramite
