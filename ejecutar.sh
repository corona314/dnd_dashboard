#!/bin/bash

# Salir si hay algún error
set -e

# Comprobar si existe el entorno virtual
if [ ! -d "venv" ]; then
    echo "No se encontró entorno virtual. Creando uno..."
    python3 -m venv venv
fi

# Activar el entorno virtual
echo "Activando entorno virtual..."
source venv/bin/activate

# Asegurarse de tener pip actualizado
echo "Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
if [ -f "requirements.txt" ]; then
    echo "Instalando dependencias de requirements.txt..."
    pip install -r requirements.txt
fi

# Ejecutar la aplicación Flask
echo "Iniciando Flask..."
export FLASK_APP=app.py
export FLASK_ENV=development
python -m flask run --host=0.0.0.0 --port=5000
