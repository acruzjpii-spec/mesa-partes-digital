"""Pruebas HTTP del servidor local de respaldo; no requieren internet."""
import json
import tempfile
import unittest
from pathlib import Path
from threading import Thread
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from respaldo_web import construir_servidor


class PruebasWebRespaldo(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.archivo = Path(self.temp.name) / 'tramites.csv'
        self.servidor = construir_servidor(0, self.archivo)
        self.hilo = Thread(target=self.servidor.serve_forever, daemon=True)
        self.hilo.start()
        self.base = f'http://127.0.0.1:{self.servidor.server_port}'

    def tearDown(self):
        self.servidor.shutdown()
        self.servidor.server_close()
        self.hilo.join(timeout=2)
        self.temp.cleanup()

    def get(self, uri):
        with urlopen(self.base + uri, timeout=3) as response:
            return response.status, response.read().decode('utf-8')

    def post(self, uri, obj):
        req = Request(self.base + uri, data=json.dumps(obj).encode(),
                      method='POST', headers={'Content-Type': 'application/json'})
        with urlopen(req, timeout=3) as response:
            return response.status, json.loads(response.read().decode('utf-8'))

    def registrar(self, asunto='Solicitud ficticia', remitente='Ana de Ejemplo'):
        return self.post('/api/respaldo/registrar', {'asunto': asunto, 'remitente': remitente})

    def test_01_interfaz_http_200(self):
        status, html = self.get('/')
        self.assertEqual(status, 200)
        self.assertIn('Mesa de Partes Digital', html)

    def test_02_lista_vacia_al_iniciar(self):
        status, body = self.get('/api/respaldo/listar')
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['expedientes'], [])

    def test_03_registrar_y_buscar_codigo(self):
        status, creado = self.registrar()
        self.assertEqual(status, 201)
        self.assertEqual(creado['codigo'], 'EXP-0001')
        status, body = self.get('/api/respaldo/buscar?codigo=exp-0001')
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body)['asunto'], 'Solicitud ficticia')

    def test_04_rechazar_asunto_invalido(self):
        with self.assertRaises(HTTPError) as ctx:
            self.registrar(asunto='a')
        self.assertEqual(ctx.exception.code, 400)
        self.assertFalse(self.archivo.exists())

    def test_05_busqueda_no_encontrada(self):
        with self.assertRaises(HTTPError) as ctx:
            self.get('/api/respaldo/buscar?codigo=EXP-NOEXISTE')
        self.assertEqual(ctx.exception.code, 404)

    def test_06_actualizar_estado_y_persistir(self):
        self.registrar()
        status, res = self.post('/api/respaldo/estado', {'codigo': 'EXP-0001', 'estado': 'atendido'})
        self.assertEqual(status, 200)
        self.assertIn('actualizado', res['mensaje'])
        self.assertIn('atendido', self.archivo.read_text(encoding='utf-8-sig'))

    def test_07_listado_ordenado(self):
        self.registrar('Segundo trámite')
        self.registrar('Otro trámite')
        self.assertEqual(
            [e['codigo'] for e in json.loads(self.get('/api/respaldo/listar')[1])['expedientes']],
            ['EXP-0001', 'EXP-0002'])

    def test_08_exportar_csv(self):
        self.registrar()
        status, body = self.get('/api/respaldo/exportar')
        self.assertEqual(status, 200)
        self.assertIn('EXP-0001', body)
        self.assertIn('remitente', body)


if __name__ == '__main__':
    unittest.main()
