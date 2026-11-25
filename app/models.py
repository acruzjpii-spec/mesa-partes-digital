from datetime import datetime
import enum
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from app.database import Base


class EstadoTramite(str, enum.Enum):
    RECIBIDO = "recibido"
    EN_PROCESO = "en_proceso"
    DERIVADO = "derivado"
    ATENDIDO = "atendido"
    ARCHIVADO = "archivado"


class Prioridad(str, enum.Enum):
    BAJA = "baja"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"


class Rol(str, enum.Enum):
    ADMIN = "admin"
    OPERADOR = "operador"
    CIUDADANO = "ciudadano"


class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)

    usuarios = relationship("Usuario", back_populates="area")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nombres = Column(String(100))
    apellidos = Column(String(100))
    rol = Column(Enum(Rol), default=Rol.CIUDADANO, nullable=False)
    area_id = Column(Integer, ForeignKey("areas.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    area = relationship("Area", back_populates="usuarios")
    movimientos = relationship("Movimiento", back_populates="usuario")


class Tramite(Base):
    __tablename__ = "tramites"

    id = Column(Integer, primary_key=True, index=True)
    codigo_seguimiento = Column(String(20), unique=True, index=True, nullable=False)
    asunto = Column(String(255), nullable=False)
    remitente_nombre = Column(String(150), nullable=False)
    remitente_email = Column(String(100))
    remitente_dni = Column(String(20))
    tipo_documento = Column(String(50))
    estado = Column(Enum(EstadoTramite), default=EstadoTramite.RECIBIDO, nullable=False)
    prioridad = Column(Enum(Prioridad), default=Prioridad.NORMAL, nullable=False)
    area_actual_id = Column(Integer, ForeignKey("areas.id"))
    fecha_recepcion = Column(DateTime, default=datetime.utcnow)
    fecha_resolucion = Column(DateTime)
    observaciones = Column(Text)

    area_actual = relationship("Area")
    documentos = relationship("Documento", back_populates="tramite", cascade="all, delete-orphan")
    movimientos = relationship("Movimiento", back_populates="tramite", cascade="all, delete-orphan")


class Documento(Base):
    __tablename__ = "documentos"

    id = Column(Integer, primary_key=True, index=True)
    tramite_id = Column(Integer, ForeignKey("tramites.id"), nullable=False)
    nombre_archivo = Column(String(255), nullable=False)
    tipo_archivo = Column(String(80))
    ruta_storage = Column(String(500), nullable=False)
    tamano_bytes = Column(Integer)
    fecha_subida = Column(DateTime, default=datetime.utcnow)

    tramite = relationship("Tramite", back_populates="documentos")


class Movimiento(Base):
    __tablename__ = "movimientos"

    id = Column(Integer, primary_key=True, index=True)
    tramite_id = Column(Integer, ForeignKey("tramites.id"), nullable=False)
    area_origen_id = Column(Integer, ForeignKey("areas.id"))
    area_destino_id = Column(Integer, ForeignKey("areas.id"))
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    accion = Column(String(100), nullable=False)
    comentario = Column(Text)
    fecha_movimiento = Column(DateTime, default=datetime.utcnow)

    tramite = relationship("Tramite", back_populates="movimientos")
    usuario = relationship("Usuario", back_populates="movimientos")
    area_origen = relationship("Area", foreign_keys=[area_origen_id])
    area_destino = relationship("Area", foreign_keys=[area_destino_id])
