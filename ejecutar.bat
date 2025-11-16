@echo off
setlocal enabledelayedexpansion

:: ---- Comprobación de dependencias ----
echo Verificando dependencias del sistema...

:: Verificar Python3
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python no está instalado. Instálalo desde https://www.python.org/downloads/
    exit /b 1
)

:: ---- Crear venv si no existe ----
if not exist venv (
    echo No se encontro entorno virtual. Creando uno...
    python -m venv venv
)

:: ---- Activar venv ----
echo Activando entorno virtual...
call venv\Scripts\activate.bat

:: ---- Actualizar pip ----
echo Actualizando pip...
python -m pip install --upgrade pip

:: ---- Instalar requirements ----
if exist requirements.txt (
    echo Instalando dependencias desde requirements.txt...
    pip install -r requirements.txt
) else (
    echo No se encontro requirements.txt, continuando...
)

:: ---- Ejecutar Flask ----
echo Iniciando Flask...
set FLASK_APP=app.py
set FLASK_ENV=development

python -m flask run --host=0.0.0.0 --port=5000