@echo off
setlocal

set "PROJECT_DIR=%~dp0.."
set "VENV_PYTHON=C:\Users\%USERNAME%\work\.venvs\sdk\Scripts\python.exe"

if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" "%PROJECT_DIR%\scripts\launch_gui.py"
) else (
    python "%PROJECT_DIR%\scripts\launch_gui.py"
)

endlocal
