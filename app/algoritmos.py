"""Algoritmos académicos complementarios: validar, buscar, ordenar y trabajar con CSV.
El registro operativo del sistema permanece en SQLite; el CSV es una exportación.
"""
import csv
from pathlib import Path

CAMPOS = ("codigo", "asunto", "remitente", "estado")


def validar_expediente(asunto: str, remitente: str, dni: str = "") -> tuple[str, str, str]:
    """Normaliza cadenas y valida datos esenciales del expediente."""
    asunto = " ".join((asunto or "").split())
    remitente = " ".join((remitente or "").split())
    dni = (dni or "").strip()
    if not 3 <= len(asunto) <= 255:
        raise ValueError("El asunto debe contener entre 3 y 255 caracteres")
    if not 3 <= len(remitente) <= 150:
        raise ValueError("El remitente debe contener entre 3 y 150 caracteres")
    if dni and (len(dni) != 8 or not dni.isdigit()):
        raise ValueError("El DNI debe tener ocho dígitos si se proporciona")
    return asunto, remitente, dni


def buscar_por_codigo(expedientes: list[dict], codigo: str) -> dict | None:
    """Búsqueda lineal sobre arreglo (demostración de fundamentos)."""
    codigo = codigo.strip().upper()
    for expediente in expedientes:
        if expediente["codigo"].upper() == codigo:
            return expediente
    return None


def ordenar_por_codigo(expedientes: list[dict]) -> list[dict]:
    """Inserción directa por código: O(n²), didáctico para listas pequeñas."""
    resultado = [dict(e) for e in expedientes]
    for i in range(1, len(resultado)):
        actual = resultado[i]
        j = i - 1
        while j >= 0 and resultado[j]["codigo"] > actual["codigo"]:
            resultado[j + 1] = resultado[j]
            j -= 1
        resultado[j + 1] = actual
    return resultado


def guardar_csv(ruta: str | Path, expedientes: list[dict]) -> None:
    """Guarda copia simple con codificación UTF-8 y encabezados."""
    ruta = Path(ruta)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    with ruta.open("w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=CAMPOS, extrasaction="ignore")
        escritor.writeheader()
        escritor.writerows(expedientes)


def leer_csv(ruta: str | Path) -> list[dict]:
    with Path(ruta).open("r", newline="", encoding="utf-8-sig") as archivo:
        return list(csv.DictReader(archivo))
