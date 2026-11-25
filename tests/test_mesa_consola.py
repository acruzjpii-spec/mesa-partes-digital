"""Casos funcionales de la alternativa de consola usando datos 100% ficticios."""
import tempfile
import unittest
from pathlib import Path
from mesa_consola import (
    actualizar_estado, consultar_expediente, generar_siguiente_codigo,
    listar_ordenados, obtener_registros, registrar_expediente,
)


class PruebasMesaConsola(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.ruta = Path(self.tmp.name) / "datos" / "expedientes.csv"

    def test_inicio_sin_archivo(self):
        self.assertEqual(obtener_registros(self.ruta), [])

    def test_registro_crea_archivo_y_codigo(self):
        nuevo = registrar_expediente(self.ruta, "Solicitud de prueba", "María Ficticia", "12345678")
        self.assertEqual(nuevo["codigo"], "EXP-0001")
        self.assertTrue(self.ruta.exists())

    def test_registro_secuencial(self):
        registrar_expediente(self.ruta, "Solicitud uno", "Persona Uno")
        nuevo = registrar_expediente(self.ruta, "Solicitud dos", "Persona Dos")
        self.assertEqual(nuevo["codigo"], "EXP-0002")

    def test_busqueda_ignora_mayusculas(self):
        registrar_expediente(self.ruta, "Solicitud uno", "Persona Uno")
        self.assertEqual(consultar_expediente(self.ruta, "exp-0001")["asunto"], "Solicitud uno")

    def test_busqueda_no_encontrado(self):
        self.assertIsNone(consultar_expediente(self.ruta, "EXP-8888"))

    def test_asunto_invalido_no_crea_archivo(self):
        with self.assertRaises(ValueError):
            registrar_expediente(self.ruta, "", "Persona Uno")
        self.assertFalse(self.ruta.exists())

    def test_dni_invalido_no_crea_archivo(self):
        with self.assertRaises(ValueError):
            registrar_expediente(self.ruta, "Solicitud uno", "Persona Uno", "12AB")
        self.assertFalse(self.ruta.exists())

    def test_persistencia_en_lectura_nueva(self):
        registrar_expediente(self.ruta, "Solicitud uno", "Persona Uno")
        self.assertEqual(len(obtener_registros(self.ruta)), 1)

    def test_estado_actualiza_y_se_guarda(self):
        registrar_expediente(self.ruta, "Solicitud uno", "Persona Uno")
        self.assertTrue(actualizar_estado(self.ruta, "exp-0001", "atendido"))
        self.assertEqual(consultar_expediente(self.ruta, "EXP-0001")["estado"], "atendido")

    def test_estado_invalido(self):
        with self.assertRaises(ValueError):
            actualizar_estado(self.ruta, "EXP-0001", "eliminado")

    def test_estado_codigo_inexistente(self):
        self.assertFalse(actualizar_estado(self.ruta, "EXP-0007", "atendido"))

    def test_listado_ordenado(self):
        registrar_expediente(self.ruta, "Solicitud uno", "Persona Uno")
        registrar_expediente(self.ruta, "Solicitud dos", "Persona Dos")
        self.assertEqual([t["codigo"] for t in listar_ordenados(self.ruta)], ["EXP-0001", "EXP-0002"])

    def test_generador_no_repite_codigo_hay_huecos(self):
        self.assertEqual(generar_siguiente_codigo([{"codigo":"EXP-0002"}, {"codigo":"EXP-0100"}]), "EXP-0101")

    def test_normaliza_cadenas(self):
        nuevo = registrar_expediente(self.ruta, "  Pedido   de  informe ", " Luis    Simulado ")
        self.assertEqual(nuevo["asunto"], "Pedido de informe")
        self.assertEqual(nuevo["remitente"], "Luis Simulado")

    def test_dni_no_persistido_por_minimizacion(self):
        registrar_expediente(self.ruta, "Solicitud uno", "Persona Uno", "12345678")
        self.assertNotIn("dni", obtener_registros(self.ruta)[0])


if __name__ == "__main__":
    unittest.main()
