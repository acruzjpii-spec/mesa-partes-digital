@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
where py >nul 2>&1
if not errorlevel 1 (
    py -3 INICIAR_WEB_PRINCIPAL.py
) else (
    python INICIAR_WEB_PRINCIPAL.py
)
set "RESULTADO=%ERRORLEVEL%"
if not "%RESULTADO%"=="0" echo Error de ejecucion. Comprueba que Python 3.10 o superior este instalado.
pause
exit /b %RESULTADO%
