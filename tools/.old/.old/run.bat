@echo off
setlocal enabledelayedexpansion

set BACKEND_PORT=8000

cd /d %~dp0
cd ..

@REM Check if .venv exists
if not exist ".venv\Scripts\activate.bat" (
    echo [VENV] No venv created, run tools\install.bat
    exit /b 1
)

@REM Run uvicorn via python -m uvicorn
echo [START] Starting uvicorn on port %BACKEND_PORT% and extra args: '%*'
.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --workers 1 --port %BACKEND_PORT% %*

endlocal
