"""Mesa de partes en consola: demostración autónoma sin librerías externas.

Complementa la aplicación web del equipo sin modificar sus rutas.
Usa funciones, validación de cadenas, listas, búsqueda, ordenamiento y archivos CSV.
Ejecutar: python mesa_consola.py
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from app.algoritmos import (
    buscar_por_codigo,
    guardar_csv,
    leer_csv,
    ordenar_por_codigo,
    validar_expediente,
)

ESTADOS = ("recibido", "en_proceso", "atendido")
ARCHIVO_DEFAULT = Path(__file__).resolve().parent / "datos" / "expedientes.csv"


def obtener_registros(ruta: str | Path = ARCHIVO_DEFAULT) -> list[dict]:
    """Lee registros persistentes o devuelve una lista vacía en primera ejecución."""
    archivo = Path(ruta)
    return leer_csv(archivo) if archivo.is_file() else []


def generar_siguiente_codigo(registros: list[dict]) -> str:
    """Genera código secuencial y evita colisiones con los códigos existentes."""
    numeros = []
    for registro in registros:
        coincidencia = re.fullmatch(r"EXP-(\d+)", registro.get("codigo", ""))
        if coincidencia:
            numeros.append(int(coincidencia.group(1)))
    siguiente = max(numeros, default=0) + 1
    return f"EXP-{siguiente:04d}"


def registrar_expediente(
    ruta: str | Path, asunto: str, remitente: str, dni: str = ""
) -> dict:
    """Valida, agrega un expediente y guarda inmediatamente el archivo CSV.

    El DNI se valida pero no se persiste en esta versión académica de consola.
    """
    asunto, remitente, _ = validar_expediente(asunto, remitente, dni)
    registros = obtener_registros(ruta)
    nuevo = {
        "codigo": generar_siguiente_codigo(registros),
        "asunto": asunto,
        "remitente": remitente,
        "estado": "recibido",
    }
    registros.append(nuevo)
    guardar_csv(ruta, registros)
    return nuevo


def consultar_expediente(ruta: str | Path, codigo: str) -> dict | None:
    return buscar_por_codigo(obtener_registros(ruta), codigo)


def listar_ordenados(ruta: str | Path) -> list[dict]:
    return ordenar_por_codigo(obtener_registros(ruta))


def actualizar_estado(ruta: str | Path, codigo: str, nuevo_estado: str) -> bool:
    estado = nuevo_estado.strip().lower()
    if estado not in ESTADOS:
        raise ValueError("Estado inválido. Opciones: recibido, en_proceso, atendido")
    registros = obtener_registros(ruta)
    expediente = buscar_por_codigo(registros, codigo)
    if expediente is None:
        return False
    expediente["estado"] = estado
    guardar_csv(ruta, registros)
    return True


def mostrar_expediente(e: dict) -> None:
    print(f"{e['codigo']} | {e['asunto']} | {e['remitente']} | {e['estado']}")


def menu(ruta: Path) -> None:
    print("\nMESA DE PARTES DIGITAL - DEMOSTRACIÓN EN CONSOLA")
    print(f"Archivo de datos: {ruta}")
    while True:
        print("\n1. Registrar   2. Buscar código   3. Listar ordenados")
        print("4. Cambiar estado   5. Salir")
        opcion = input("Elige una opción: ").strip()
        if opcion == "1":
            asunto = input("Asunto: ")
            remitente = input("Remitente: ")
            dni = input("DNI (8 dígitos): ")
            try:
                nuevo = registrar_expediente(ruta, asunto, remitente, dni)
                print("REGISTRO CORRECTO - Código:", nuevo["codigo"])
            except ValueError as e:
                print("ERROR DE VALIDACIÓN:", e)
        elif opcion == "2":
            codigo = input("Código a buscar: ")
            resultado = consultar_expediente(ruta, codigo)
            mostrar_expediente(resultado) if resultado else print("NO ENCONTRADO")
        elif opcion == "3":
            registros = listar_ordenados(ruta)
            if not registros:
                print("Todavía no hay expedientes registrados")
            for registro in registros:
                mostrar_expediente(registro)
            print("Total:", len(registros))
        elif opcion == "4":
            codigo = input("Código: ")
            estado = input("Estado (recibido/en_proceso/atendido): ")
            try:
                print("ESTADO ACTUALIZADO" if actualizar_estado(ruta, codigo, estado) else "NO ENCONTRADO")
            except ValueError as e:
                print("ERROR DE VALIDACIÓN:", e)
        elif opcion == "5":
            print("Fin de la demostración. Datos conservados en CSV.")
            return
        else:
            print("Opción no reconocida")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mesa de partes de práctica, sin instalación extra")
    parser.add_argument("--archivo", type=Path, default=ARCHIVO_DEFAULT)
    argumentos = parser.parse_args()
    menu(argumentos.archivo)
