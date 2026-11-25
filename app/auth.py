import os
import secrets
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime, timedelta
from typing import Iterable, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Rol, Usuario

_configured_key = os.environ.get("SECRET_KEY", "")
SECRET_KEY = _configured_key if len(_configured_key) >= 32 and not _configured_key.startswith("REEMPLAZAR") else secrets.token_urlsafe(48)
# Si falta SECRET_KEY válida, se genera una clave temporal por proceso.
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: Optional[str] = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(Usuario).filter(Usuario.username == username).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_role(roles: Iterable[Rol | str]):
    allowed = {r.value if isinstance(r, Rol) else r for r in roles}

    def role_checker(current_user: Usuario = Depends(get_current_user)) -> Usuario:
        user_role = current_user.rol.value if isinstance(current_user.rol, Rol) else str(current_user.rol)
        if user_role not in allowed:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tiene permisos para esta acción")
        return current_user

    return role_checker
