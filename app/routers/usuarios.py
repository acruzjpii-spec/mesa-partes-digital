from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.auth import create_access_token, get_current_user, get_password_hash, require_role, verify_password
from app.database import get_db
from app.models import Area, Rol, Usuario
from app.schemas import AreaBase, AreaResponse, LoginRequest, Token, UsuarioCreate, UsuarioResponse

router = APIRouter(prefix="/api", tags=["Usuarios y áreas"])


@router.post("/auth/register", response_model=UsuarioResponse)
def register(user: UsuarioCreate, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.username == user.username).first():
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    if db.query(Usuario).filter(Usuario.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email ya registrado")
    db_user = Usuario(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password),
        nombres=user.nombres,
        apellidos=user.apellidos,
        rol=Rol.CIUDADANO,  # Nunca confiar en el rol solicitado por un registro público.
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/auth/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    token = create_access_token(data={"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/usuarios/me", response_model=UsuarioResponse)
def me(current_user: Usuario = Depends(get_current_user)):
    return current_user


@router.get("/areas", response_model=list[AreaResponse])
def listar_areas(db: Session = Depends(get_db)):
    return db.query(Area).all()


@router.post("/areas", response_model=AreaResponse)
def crear_area(area: AreaBase, db: Session = Depends(get_db), _=Depends(require_role([Rol.ADMIN]))):
    db_area = Area(nombre=area.nombre, descripcion=area.descripcion)
    db.add(db_area)
    db.commit()
    db.refresh(db_area)
    return db_area
