#!/bin/bash

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "Activando entorno virtual..."
    source venv/bin/activate
else
    echo "No se encontró entorno virtual. Se usará el Python global."
fi

# Instalar paquetes si no están instalados
if [ -f "requirements.txt" ]; then
    echo "Instalando dependencias de requirements.txt..."
    pip install -r requirements.txt
fi

# Ejecutar la aplicación Flask
echo "Iniciando Flask..."
export FLASK_APP=app.py
export FLASK_ENV=development
python3 -m flask run --host=0.0.0.0 --port=5000
