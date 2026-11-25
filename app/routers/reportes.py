from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.auth import require_role
from app.database import get_db
from app.models import Rol, Tramite

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])


@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db), _=Depends(require_role([Rol.ADMIN, Rol.OPERADOR]))):
    total = db.query(Tramite).count()
    por_estado = db.query(Tramite.estado, func.count(Tramite.id)).group_by(Tramite.estado).all()
    por_prioridad = db.query(Tramite.prioridad, func.count(Tramite.id)).group_by(Tramite.prioridad).all()
    recientes = db.query(Tramite).order_by(Tramite.fecha_recepcion.desc()).limit(5).all()
    return {
        "total_tramites": total,
        "por_estado": {estado.value: cantidad for estado, cantidad in por_estado},
        "por_prioridad": {prioridad.value: cantidad for prioridad, cantidad in por_prioridad},
        "recientes": recientes,
    }
