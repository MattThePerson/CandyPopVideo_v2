@echo off
REM Installs npm and python deps

REM cd into frontend directory and install npm deps
cd frontend
npm install
cd ..

REM create venv if it doesn't exist
if not exist ".venv\Scripts\activate.bat" (
    python -m venv .venv
)

REM activate venv
call .venv\Scripts\activate.bat

REM upgrade pip and install python deps
python -m pip install --upgrade pip
pip install -r requirements.txt
