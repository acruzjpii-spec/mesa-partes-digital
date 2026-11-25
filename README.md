# Mesa de Partes Digital — evaluación final

Prototipo académico de Fundamentos de Programación (CIIN1205P). Registra, valida, busca, ordena y almacena expedientes.

## Demostración recomendada (Windows)
1. Descarga el código (Code > Download ZIP) y descomprime. Instala Python 3.10 o superior (3.11 o 3.12 recomendado).
2. Abre esta carpeta y ejecuta `PROBAR_CODIGO.bat`. Debe mostrar 31 pruebas y OK.
3. Ejecuta `INICIAR_WEB_RESPALDO.bat`. Abre http://127.0.0.1:8765/ si no se abre automáticamente. No requiere internet ni paquetes adicionales.
4. Registra, busca, actualiza y exporta. Usa solo datos ficticios. Deja la terminal abierta; Ctrl+C para detener.
5. Alternativa: `INICIAR_CONSOLA.bat`.

## Aplicación web principal
Ejecuta `INICIAR_WEB_PRINCIPAL.bat` (primera vez requiere internet para instalar dependencias). Genera un entorno virtual y credenciales locales; muestra la contraseña de admin en la terminal. Abre http://127.0.0.1:8000/static/index.html. API: http://127.0.0.1:8000/docs. Esta aplicación usa FastAPI, SQLAlchemy y SQLite. No se ha revalidado su instalación en Windows en esta revisión.

## Terminal (desde esta carpeta)
- `python -m unittest discover -s tests -v`
- `python respaldo_web.py`
- `python mesa_consola.py`

## Pruebas y alcance
El 25 de noviembre de 2026 se ejecutaron localmente las 31 pruebas de algoritmos, consola y servidor web de respaldo, con resultado OK. Consulta Resultado_31_pruebas.txt y reproduce la ejecución. No es una certificación de la aplicación FastAPI, de seguridad ni de producción.

El respaldo usa CSV y valida el DNI opcional sin almacenarlo. Los datos de la web de respaldo quedan en datos/respaldo_web.csv; la consola utiliza datos/expedientes.csv. No son la misma base que SQLite. Los estados del respaldo son recibido, en_proceso y atendido. No publicar .env, datos reales, bases locales ni adjuntos. Uso académico local, no producción.

## Historial
Se conserva el commit inicial existente. El código de evaluación final se publicó el 25 de noviembre de 2026 en commits agrupados por componentes. No se reconstruyeron ni se retrofecharon commits históricos de desarrollo.
