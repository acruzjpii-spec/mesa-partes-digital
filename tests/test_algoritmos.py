"""Pruebas reproducibles sin dependencias externas: python -m unittest discover -s tests -v."""
import tempfile
import unittest
from pathlib import Path
from app.algoritmos import buscar_por_codigo, guardar_csv, leer_csv, ordenar_por_codigo, validar_expediente

DATOS = [
    {"codigo": "EXP-003", "asunto": "Tercero", "remitente": "Elena Prueba", "estado": "recibido"},
    {"codigo": "EXP-001", "asunto": "Primero", "remitente": "Luis Prueba", "estado": "atendido"},
    {"codigo": "EXP-002", "asunto": "Segundo", "remitente": "Ana Prueba", "estado": "en_proceso"},
]


class PruebasAlgoritmos(unittest.TestCase):
    def test_validacion_normaliza_texto(self):
        self.assertEqual(validar_expediente("  Solicitud   de   prueba ", " Ana   Ejemplo ", "12345678"),
                         ("Solicitud de prueba", "Ana Ejemplo", "12345678"))

    def test_validacion_rechaza_asunto_vacio(self):
        with self.assertRaises(ValueError): validar_expediente("  ", "Ana Ejemplo")

    def test_validacion_rechaza_dni_invalido(self):
        with self.assertRaises(ValueError): validar_expediente("Solicitud", "Ana Ejemplo", "12X45678")

    def test_busqueda_encuentra_codigo(self):
        self.assertEqual(buscar_por_codigo(DATOS, "exp-002")["asunto"], "Segundo")

    def test_busqueda_inexistente(self):
        self.assertIsNone(buscar_por_codigo(DATOS, "EXP-999"))

    def test_ordenamiento_mantiene_entrada_original(self):
        codigos = [x["codigo"] for x in ordenar_por_codigo(DATOS)]
        self.assertEqual(codigos, ["EXP-001", "EXP-002", "EXP-003"])
        self.assertEqual(DATOS[0]["codigo"], "EXP-003")

    def test_guardado_lectura_csv(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "subcarpeta" / "expedientes.csv"
            guardar_csv(ruta, DATOS)
            self.assertEqual(leer_csv(ruta), DATOS)

    def test_guardado_sobrescribe_sin_duplicar(self):
        with tempfile.TemporaryDirectory() as carpeta:
            ruta = Path(carpeta) / "expedientes.csv"
            guardar_csv(ruta, DATOS)
            guardar_csv(ruta, DATOS)
            self.assertEqual(len(leer_csv(ruta)), 3)

if __name__ == "__main__": unittest.main()
