@echo off
cd /d "%~dp0"
if not exist ".venv" (
    echo Creando entorno de Python la primera vez, espera un momento...
    python -m venv .venv
    call .venv\Scripts\activate.bat
    pip install --quiet -r requirements.txt
) else (
    call .venv\Scripts\activate.bat
)
streamlit run frontend\app.py
pause
