import os
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from app.auth import get_password_hash
from app.database import Base, SessionLocal, engine
from app.models import Area, Rol, Tramite, Usuario
from app.routers import reportes, tramites, usuarios

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Mesa de Partes Digital",
    description="Sistema de gestión documental para recepción, seguimiento y trazabilidad de trámites",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def init_db():
    db = SessionLocal()
    try:
        if not db.query(Area).first():
            areas = [
                Area(nombre="Mesa de Partes", descripcion="Recepción inicial de documentos"),
                Area(nombre="Secretaría General", descripcion="Coordinación institucional"),
                Area(nombre="Archivo Central", descripcion="Custodia documental"),
                Area(nombre="Legal", descripcion="Asesoría jurídica"),
            ]
            db.add_all(areas)
            db.commit()

        admin_password = os.environ.get("ADMIN_PASSWORD")
        if admin_password and len(admin_password) >= 12 and not admin_password.startswith("REEMPLAZAR") and not db.query(Usuario).filter(Usuario.username == "admin").first():
            db.add(Usuario(username="admin", email="admin@example.com", password_hash=get_password_hash(admin_password), nombres="Administrador", apellidos="Sistema", rol=Rol.ADMIN))
            db.commit()
    finally:
        db.close()


init_db()

app.include_router(usuarios.router)
app.include_router(tramites.router)
app.include_router(reportes.router)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")
