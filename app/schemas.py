from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from app.models import EstadoTramite, Prioridad, Rol


class UsuarioBase(BaseModel):
    username: str
    email: EmailStr
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    rol: Rol = Rol.CIUDADANO


class UsuarioCreate(UsuarioBase):
    password: str


class UsuarioResponse(UsuarioBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class AreaBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class AreaResponse(AreaBase):
    id: int

    class Config:
        from_attributes = True


class DocumentoResponse(BaseModel):
    id: int
    nombre_archivo: str
    tipo_archivo: Optional[str] = None
    tamano_bytes: Optional[int] = None
    fecha_subida: datetime

    class Config:
        from_attributes = True


class MovimientoResponse(BaseModel):
    id: int
    accion: str
    comentario: Optional[str] = None
    fecha_movimiento: datetime
    area_origen: Optional[AreaResponse] = None
    area_destino: Optional[AreaResponse] = None

    class Config:
        from_attributes = True


class TramiteUpdate(BaseModel):
    estado: Optional[EstadoTramite] = None
    area_actual_id: Optional[int] = None
    observaciones: Optional[str] = None


class TramiteResponse(BaseModel):
    id: int
    codigo_seguimiento: str
    asunto: str
    remitente_nombre: str
    remitente_email: Optional[EmailStr] = None
    remitente_dni: Optional[str] = None
    tipo_documento: Optional[str] = None
    estado: EstadoTramite
    prioridad: Prioridad
    fecha_recepcion: datetime
    fecha_resolucion: Optional[datetime] = None
    observaciones: Optional[str] = None
    area_actual: Optional[AreaResponse] = None
    documentos: List[DocumentoResponse] = []
    movimientos: List[MovimientoResponse] = []

    class Config:
        from_attributes = True


class SeguimientoResponse(BaseModel):
    codigo_seguimiento: str
    asunto: str
    estado: EstadoTramite
    fecha_recepcion: datetime
    area_actual: Optional[str] = None
    movimientos: List[MovimientoResponse] = []


class LoginRequest(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str
