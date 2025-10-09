#!/bin/bash

# Salir si hay algún error
set -e

# --- Funciones auxiliares ---
function instalar_si_no_existe() {
    local paquete=$1
    if ! dpkg -s "$paquete" &> /dev/null; then
        echo "Instalando paquete: $paquete..."
        sudo apt-get update -y
        sudo apt-get install -y "$paquete"
    fi
}

# --- Comprobaciones previas ---
echo "Verificando dependencias del sistema..."

# Asegurar Python3, pip y venv
instalar_si_no_existe "python3"
instalar_si_no_existe "python3-pip"
instalar_si_no_existe "python3-venv"

# --- Crear entorno virtual si no existe ---
if [ ! -d "venv" ]; then
    echo "No se encontró entorno virtual. Creando uno..."
    python3 -m venv venv
fi

# --- Activar entorno virtual ---
echo "Activando entorno virtual..."
source venv/bin/activate

# --- Actualizar pip ---
echo "Actualizando pip..."
pip install --upgrade pip

# --- Instalar dependencias ---
if [ -f "requirements.txt" ]; then
    echo "Instalando dependencias desde requirements.txt..."
    pip install -r requirements.txt
else
    echo "No se encontró requirements.txt, continuando..."
fi

# --- Ejecutar aplicación Flask ---
echo "Iniciando Flask..."
export FLASK_APP=app.py
export FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=5000