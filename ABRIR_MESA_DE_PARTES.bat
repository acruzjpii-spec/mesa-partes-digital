@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"
if not exist "mesa_escritorio.py" goto incompleto
py -3 -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if not errorlevel 1 goto usar_py
python -c "import sys; sys.exit(0 if sys.version_info >= (3,10) else 1)" >nul 2>&1
if not errorlevel 1 goto usar_python
echo ERROR: Instala Python 3.10 o superior desde python.org y marca Add Python to PATH.
goto terminar
:usar_py
py -3 mesa_escritorio.py
goto resultado
:usar_python
python mesa_escritorio.py
goto resultado
:incompleto
echo ERROR: Descomprime TODO el ZIP en una carpeta antes de ejecutar.
goto terminar
:resultado
if errorlevel 1 echo ERROR: Envia una captura del mensaje anterior.
:terminar
echo.
pause
