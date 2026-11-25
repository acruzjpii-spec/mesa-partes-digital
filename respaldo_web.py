"""Servidor web académico local de respaldo, sin dependencias externas.

No es la API principal FastAPI. Ofrece en localhost las operaciones del
curso desde un navegador y guarda los expedientes en un CSV.
Ejecutar: python respaldo_web.py
"""
from __future__ import annotations

import argparse
import csv
import io
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import webbrowser
from threading import Thread
from mesa_consola import (
    consultar_expediente, listar_ordenados, registrar_expediente,
    actualizar_estado, obtener_registros,
)

ROOT = Path(__file__).resolve().parent
ARCHIVO = ROOT / 'datos' / 'respaldo_web.csv'
HTML = ROOT / 'static' / 'respaldo.html'
MAX_JSON = 16_384


def construir_servidor(puerto: int = 8765, archivo: str | Path = ARCHIVO) -> ThreadingHTTPServer:
    """Permite usar un archivo temporal en pruebas sin modificar datos reales."""
    datos = Path(archivo)

    class Handler(BaseHTTPRequestHandler):
        server_version = 'MesaDePartesAcademica/1.0'

        def log_message(self, fmt: str, *args: object) -> None:
            print('[WEB RESPALDO] ' + fmt % args)

        def responder(self, code: int, obj: dict | list) -> None:
            data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
            self.send_response(code)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_GET(self) -> None:
            req = urlsplit(self.path)
            if req.path in ('/', '/respaldo.html'):
                data = HTML.read_bytes()
                self.send_response(200)
                self.send_header('Content-Type','text/html; charset=utf-8')
                self.send_header('Cache-Control','no-store')
                self.send_header('Content-Length',str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            elif req.path == '/api/respaldo/listar':
                self.responder(200, {'expedientes': listar_ordenados(datos)})
            elif req.path == '/api/respaldo/buscar':
                codigo = parse_qs(req.query).get('codigo',[''])[0]
                encontrado = consultar_expediente(datos,codigo)
                self.responder(200, encontrado) if encontrado else self.responder(404, {'error':'Código no encontrado'})
            elif req.path == '/api/respaldo/exportar':
                registros = listar_ordenados(datos)
                buf = io.StringIO(newline='')
                escritor = csv.DictWriter(buf, fieldnames=['codigo','asunto','remitente','estado'])
                escritor.writeheader()
                escritor.writerows(registros)
                data = ('\ufeff' + buf.getvalue()).encode('utf-8')
                self.send_response(200)
                self.send_header('Content-Type','text/csv; charset=utf-8')
                self.send_header('Content-Disposition','attachment; filename="mesa_de_partes_respaldo.csv"')
                self.send_header('Content-Length',str(len(data)))
                self.end_headers()
                self.wfile.write(data)
            else:
                self.responder(404, {'error':'Recurso no encontrado'})

        def do_POST(self) -> None:
            req = urlsplit(self.path)
            if req.path not in ('/api/respaldo/registrar','/api/respaldo/estado'):
                self.responder(404, {'error':'Recurso no encontrado'})
                return
            try:
                cantidad = int(self.headers.get('Content-Length','0'))
                if not 0 < cantidad <= MAX_JSON:
                    self.responder(413,{'error':'Datos de entrada demasiado extensos'})
                    return
                cuerpo = json.loads(self.rfile.read(cantidad))
                if not isinstance(cuerpo,dict):
                    raise ValueError('Se requiere un objeto JSON')
                if req.path.endswith('/registrar'):
                    nuevo = registrar_expediente(
                        datos, str(cuerpo.get('asunto','')),
                        str(cuerpo.get('remitente','')),
                        str(cuerpo.get('dni','')),
                    )
                    self.responder(201, nuevo)
                else:
                    ok = actualizar_estado(datos, str(cuerpo.get('codigo','')),
                                           str(cuerpo.get('estado','')))
                    if not ok:
                        self.responder(404, {'error':'Código no encontrado'})
                    else:
                        self.responder(200,{'mensaje':'Estado actualizado'})
            except (ValueError,TypeError,json.JSONDecodeError) as exc:
                self.responder(400, {'error':str(exc)})

    server = ThreadingHTTPServer(('127.0.0.1',puerto),Handler)
    return server


def main() -> None:
    parser = argparse.ArgumentParser(description='Web de respaldo sin internet; solo demostración académica local')
    parser.add_argument('--puerto', type=int, default=8765)
    parser.add_argument('--archivo', type=Path, default=ARCHIVO)
    args = parser.parse_args()
    if not HTML.is_file():
        raise FileNotFoundError("Falta static/respaldo.html. Extrae todo el ZIP antes de abrirlo.")
    try:
        server = construir_servidor(args.puerto,args.archivo)
    except OSError:
        if args.puerto == 0:
            raise
        print("Puerto ocupado o no disponible; buscando otro puerto local...", flush=True)
        server = construir_servidor(0,args.archivo)
    url = f'http://127.0.0.1:{server.server_port}/'
    print('\nMESA DE PARTES | RESPALDO WEB SIN INTERNET',flush=True)
    print('Abre en el navegador:',url,flush=True)
    print('Los datos se guardan en:',args.archivo,flush=True)
    print('Solo usar nombres ficticios y datos de práctica.',flush=True)
    print('CTRL+C para detener el servidor.\n',flush=True)
    def abrir_navegador():
        try:
            if not webbrowser.open(url):
                print("Abre manualmente esta direccion: " + url, flush=True)
        except Exception as exc:
            print("No se pudo abrir el navegador: " + str(exc), flush=True)
    Thread(target=abrir_navegador, daemon=True).start()
    try:
        server.serve_forever(poll_interval=0.1)
    except KeyboardInterrupt:
        print('\nServidor de respaldo detenido.')
    finally:
        server.server_close()

if __name__ == '__main__':
    main()
