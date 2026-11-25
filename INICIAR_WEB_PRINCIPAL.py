#!/usr/bin/env python3
"""Launcher local, estándar de Python, para el prototipo académico."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import time
from urllib.request import urlopen
import webbrowser

RAIZ = Path(__file__).resolve().parent
SISTEMA = RAIZ
REQUISITOS = SISTEMA / 'requirements.txt'
ENTORNO = SISTEMA / '.venv'
PYTHON_VENV = ENTORNO / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
MARCADOR = ENTORNO / '.mesa_dependencias_ok'
WEB = 'http://127.0.0.1:8000'


def ejecutar(comando, *, cwd=RAIZ):
    print('\n> ' + ' '.join(map(str, comando)), flush=True)
    subprocess.run([str(c) for c in comando], cwd=cwd, check=True)


def preparar_entorno():
    if not PYTHON_VENV.exists():
        print('\n[1/4] Preparando entorno virtual de Python (solo primera vez)...', flush=True)
        ejecutar([sys.executable, '-m', 'venv', str(ENTORNO)])
    else:
        print('\n[1/4] Entorno de Python encontrado.', flush=True)
    firma = hashlib.sha256(REQUISITOS.read_bytes()).hexdigest()
    if not MARCADOR.exists() or MARCADOR.read_text(encoding='utf-8').strip() != firma:
        print('\n[2/4] Instalando dependencias; la primera vez requiere internet...', flush=True)
        ejecutar([PYTHON_VENV, '-m', 'pip', 'install', '--disable-pip-version-check', '-r', REQUISITOS], cwd=SISTEMA)
        MARCADOR.write_text(firma, encoding='utf-8')
    else:
        print('[2/4] Dependencias ya preparadas.', flush=True)


def credenciales_locales():
    ruta = SISTEMA / '.env'
    if not ruta.exists():
        clave = secrets.token_urlsafe(48)
        pass_admin = secrets.token_urlsafe(18)
        ruta.write_text('SECRET_KEY=' + clave + '\nADMIN_PASSWORD=' + pass_admin + '\n', encoding='utf-8')
        print('\n[3/4] Datos de acceso de demostracion creados en .env', flush=True)
    else:
        print('\n[3/4] Configuracion de demostracion ya existe.', flush=True)
    try:
        config = dict(line.split('=', 1) for line in ruta.read_text(encoding='utf-8').splitlines() if '=' in line and not line.startswith('#'))
        print('   Usuario: admin', flush=True)
        print('   Contrasena local: ' + config.get('ADMIN_PASSWORD', '[revisar .env]'), flush=True)
    except Exception:
        print('   Revisa la contrasena en .env', flush=True)


def url_esta_lista():
    try:
        with urlopen(WEB + '/openapi.json', timeout=1.2) as resp:
            d = json.loads(resp.read())
        return d.get('info', {}).get('title') == 'Mesa de Partes Digital'
    except Exception:
        return False


def puerto_ocupado():
    try:
        with socket.create_connection(('127.0.0.1', 8000), timeout=0.8):
            return True
    except OSError:
        return False


def abrir_pestanas():
    print('\nAbriendo sistema local...', flush=True)
    webbrowser.open(WEB + '/static/index.html', new=2)
    print('Sistema: ' + WEB + '/static/index.html', flush=True)
    print('API: ' + WEB + '/docs', flush=True)


def main():
    print('\n=== MESA DE PARTES DIGITAL | MODO EXPOSICION ===', flush=True)
    print('Python detectado: ' + sys.version.split()[0], flush=True)
    print('Carpeta: ' + str(RAIZ), flush=True)
    if sys.version_info < (3, 10):
        print('ERROR: Se necesita Python 3.10 o superior.', flush=True)
        return 2
    preparar_entorno()
    credenciales_locales()
    if puerto_ocupado():
        if url_esta_lista():
            print('[4/4] Ya hay una Mesa de Partes activa en el puerto 8000.', flush=True)
            abrir_pestanas()
            return 0
        print('ERROR: El puerto 8000 esta ocupado por otro programa. Cierralo y vuelve a intentar.', flush=True)
        return 3
    print('\n[4/4] Iniciando el servidor local...', flush=True)
    proc = subprocess.Popen([str(PYTHON_VENV), '-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'], cwd=SISTEMA)
    try:
        for _ in range(60):
            if proc.poll() is not None:
                print('ERROR: El servidor termino. Mira el error de Python que aparece arriba.', flush=True)
                return proc.returncode or 4
            if url_esta_lista():
                abrir_pestanas()
                print('\nSistema activo. Deja esta ventana ABIERTA durante la exposicion.', flush=True)
                print('Para detenerlo: CTRL + C, o cierra la ventana al finalizar.', flush=True)
                proc.wait()
                return proc.returncode or 0
            time.sleep(1)
        print('ERROR: El servidor no respondio en 60 segundos.', flush=True)
        return 5
    except KeyboardInterrupt:
        print('\nCerrando el sistema...', flush=True)
        return 0
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as ex:
        print('\nERROR al preparar Python o instalar las librerias.', flush=True)
        print('Si es la primera vez, comprueba que tienes internet y usa Python 3.11 o 3.12.', flush=True)
        raise SystemExit(ex.returncode or 1)
    except Exception as ex:
        print('\nERROR: ' + str(ex), flush=True)
        raise SystemExit(1)
