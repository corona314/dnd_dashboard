# DnD Dashboard

## ¿Qué es este proyecto?

Este proyecto es una pequeña aplicación web para ayudar a llevar el control de una partida de Dungeons & Dragons durante una sesión de combate. Permite gestionar personajes, enemigos, estados, daño, shock, iniciativa y ronda desde una interfaz sencilla.

## ¿Para qué sirve?

Sirve como tablero de referencia en vivo para el Dungeon Master o para cualquier jugador que quiera tener una vista rápida del estado de la batalla. Se puede usar para:

- controlar la vida de los personajes y enemigos
- aplicar heridas y shock (mecánica Homebrew propia)
- marcar quién tiene el turno actual
- añadir estados como aturdido, invisible, incapacitado o cansancio
- llevar la cuenta de la ronda actual
- importar enemigos desde la API de Open5e

## ¿Cómo está hecho?

La aplicación está construida con:

- Python y Flask para el servidor web
- Jinja2 para renderizar las plantillas HTML
- JavaScript vanilla para actualizar la interfaz dinámicamente
- JSON para almacenar los datos de los personajes y la ronda
- CSS para el estilo del panel de control y del dashboard

## Estructura del proyecto

- app.py: contiene la lógica del servidor, las rutas y la gestión de datos
- templates/: plantillas HTML para las páginas de control y dashboard
- static/: archivos CSS, imágenes y datos auxiliares como descripciones de estados
- personajes.json: archivo donde se guardan los personajes y la ronda actual
- requirements.txt: dependencias del proyecto

## Páginas principales

- /control: pantalla para gestionar personajes, estados y combate
- /dashboard: vista resumida para mostrar el estado de los participantes en tiempo real

## Requisitos

Tener Python instalado y las dependencias del proyecto.

## Instalación

```bash
pip install -r requirements.txt
```

## Ejecución

Puedes lanzar la aplicación con cualquiera de estas opciones:

```bash
python app.py
```

O ejecutar el script incluido:

```bash
./ejecutar.sh
```

En Windows también puedes usar:

```bat
ejecutar.bat
```

## Notas

La aplicación guarda la información en el archivo personajes.json, por lo que los cambios se mantienen entre ejecuciones.
