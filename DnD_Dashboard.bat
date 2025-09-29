@echo off
call "%~dp0venv\Scripts\activate.bat"

python -c "import flask" 2>nul
if errorlevel 1 (
    echo Flask no encontrado. Instalando...
    pip install flask
)

python "%~dp0app.py"
pause
