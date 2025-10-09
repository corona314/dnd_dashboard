import random
from flask import Flask, render_template, request, jsonify
import json
import requests

# Flask
app = Flask(__name__)

def cargar_personajes():
    try:
        with open("personajes.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("personajes", [])   
    except FileNotFoundError:
        return []

def cargar_ronda():
    try:
        with open("personajes.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("ronda", 0)
    except FileNotFoundError:
        return 0

def guardar_personajes(personajes):
    try:
        with open("personajes.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            ronda = data.get("ronda", 0) 
    except FileNotFoundError:
        ronda = 0

    with open("personajes.json", "w", encoding="utf-8") as f:
        json.dump({"ronda": ronda, "personajes": personajes}, f, ensure_ascii=False, indent=4)


def guardar_ronda(ronda):
    try:
        with open("personajes.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            personajes_actuales = data.get("personajes", [])
    except FileNotFoundError:
        personajes_actuales = []

    with open("personajes.json", "w", encoding="utf-8") as f:
        json.dump({"ronda": ronda, "personajes": personajes_actuales}, f, ensure_ascii=False, indent=4)

guardar_ronda(0) # Inicializar ronda en 0

@app.route("/dashboard")
def dashboard():
    personajes = cargar_personajes()
    ronda = cargar_ronda()

    return render_template("dashboard.html", personajes=personajes, ronda=ronda)

@app.route("/control")
def control():
    return render_template("control.html")

@app.route("/actualizar", methods=["POST"])
def actualizar():
    data = request.json
    personajes = cargar_personajes()
    ronda_actual = cargar_ronda()

    # Actualizar turnos si se envía
    if "turno" in data:
        for p in personajes:
            p["turno"] = (p["nombre"] == data["turno"])

    # Actualizar cada personaje según el nombre
    if "nombre" in data:
        for p in personajes:
            if p["nombre"] == data["nombre"]:
                if "vida_max" in data:
                    p["vida_max"] = max(1, data["vida_max"])
                    # Ajustar vida_actual si excede
                    if p["vida_actual"] > p["vida_max"]:
                        p["vida_actual"] = p["vida_max"]
                if "vida_actual" in data:
                    p["vida_actual"] = max(0, min(p["vida_max"], data["vida_actual"]))
                if "heridas" in data:
                    heridas_antes = p.get("heridas", 0)
                    p["heridas"] = max(0, data["heridas"])
                    # lógica shock exacta
                    if p["heridas"] < 4:
                        p["shock"] = 0
                    elif p["heridas"] > 3:
                        nuevas_heridas = max(0, p["heridas"] - max(3, heridas_antes))
                        p["shock"] = min(3, p.get("shock", 0) + nuevas_heridas)
                if "shock" in data:
                    p["shock"] = max(0, min(3, data["shock"]))
                if "iniciativa" in data:
                    p["iniciativa"] = data["iniciativa"]
                    
    if "estado_accion" in data and "estado" in data and "nombre" in data:
        estado = data["estado"]
        accion = data["estado_accion"]
        for p in personajes:
            if p["nombre"] == data["nombre"]:
                if "estados" not in p:
                    p["estados"] = []
                if accion == "agregar":
                    if estado == "Cansancio":
                        niveles = [s for s in p["estados"] if s.startswith("Cansancio")]
                        if niveles:
                            actual = niveles[0]
                            p["estados"].remove(actual)
                            if actual == "Cansancio":
                                p["estados"].append("Cansancio (2)")
                            elif actual == "Cansancio (2)":
                                p["estados"].append("Cansancio (3)")
                            elif actual == "Cansancio (3)":
                                p["estados"].append("Cansancio (4)")
                            elif actual == "Cansancio (4)":
                                p["estados"].append("Cansancio (5)")
                            elif actual == "Cansancio (5)":
                                p["estados"].append("Cansancio (6)")
                        else:
                            p["estados"].append("Cansancio")
                    elif "(" in estado and ")" in estado:  # cualquier enfermedad con niveles
                        base_estado = estado.split(" (")[0]
                        # Eliminar el estado previo de esa enfermedad
                        p["estados"] = [s for s in p["estados"] if not s.startswith(base_estado)]
                        p["estados"].append(estado)
                    else:  # estados normales
                        if estado not in p["estados"]:
                            p["estados"].append(estado)
                        if estado in ["Aturdido", "Inconsciente", "Paralizado", "Petrificado"] and "Incapacitado" not in p["estados"]:
                            p["estados"].append("Incapacitado")

                elif accion == "quitar":
                    if estado == "Cansancio":
                        p["estados"] = [s for s in p["estados"] if not s.startswith("Cansancio")]
                    else:
                        if estado in p["estados"]:
                            p["estados"].remove(estado)
                    if estado in ["Aturdido", "Inconsciente", "Paralizado", "Petrificado"] and "Incapacitado" in p["estados"]:
                        p["estados"].remove("Incapacitado")

    # Actualizar ronda si se envía
    if "ronda" in data:
        ronda_actual = data["ronda"]

    personaje_accion = data.get("personaje_accion")
    nombre = data.get("nombre")

    # Agregar personaje
    if personaje_accion == "agregar" and nombre and "tipo" in data:
        tipo = data["tipo"]
        if tipo == "Personaje": tipo = "character"
        elif tipo == "Enemigo": tipo = "enemy"
        elif tipo == "NPC": tipo = "npc"
        nuevo_personaje = {
            "nombre": nombre,
            "vida_actual": 50,
            "vida_max": 50,
            "heridas": 0,
            "shock": 0,
            "imagen": tipo+".png",
            "estados": [],
            "iniciativa": 1,
            "turno": False,
            "tipo": tipo,
        }
        personajes.append(nuevo_personaje)

    # Eliminar personaje
    elif personaje_accion == "eliminar" and nombre:
        personajes = [p for p in personajes if p["nombre"] != nombre]

    guardar_personajes(personajes)
    guardar_ronda(ronda_actual)
    return jsonify({"status": "ok"})

@app.route("/dashboard-data")
def dashboard_data():
    personajes = cargar_personajes()
    ronda = cargar_ronda()
    # Ordenar por iniciativa
    personajes_ordenados = sorted(personajes, key=lambda p: p.get("iniciativa", 0), reverse=True)
    return jsonify({
        "ronda": ronda,
        "personajes": personajes_ordenados
    })


@app.route("/api/enemigo", methods=["POST"])
def agregar_enemigo_api():
    data = request.get_json()
    nombre = data.get("nombre")

    if not nombre:
        return jsonify({"error": "Debe proporcionar un nombre"}), 400

    # Llamar a la API
    resp = requests.get("https://api.open5e.com/monsters/", params={"search": nombre})
    if resp.status_code != 200:
        return jsonify({"error": "No se pudo obtener datos de la API"}), 500

    resultados = resp.json().get("results", [])
    if not resultados:
        return jsonify({"error": f"No se encontró ningún enemigo llamado '{nombre}'"}), 404

    # Tomamos el primer resultado que coincida
    monster = resultados[0]

    # Extraer atributos
    vida_max = monster.get("hit_points", 10)

    personajes = cargar_personajes()

    # Generar nombre único
    nombre_base = nombre.strip()
    contador = 1
    nombres_existentes = [p["nombre"].lower() for p in personajes]

    while nombre.lower() in nombres_existentes:
        nombre = f"{nombre_base}{contador}"
        contador += 1
    
    # Crear nuevo enemigo
    nuevo = {
        "nombre": nombre,
        "vida_actual": vida_max,
        "vida_max": vida_max,
        "heridas": 0,
        "shock": 0,
        "imagen": "enemy.png",
        "estados": [],
        "iniciativa": random.randint(1,20)+(monster.get("dexterity")-10)/2,
        "turno": False,
        "tipo": "enemy"
    }

    personajes.append(nuevo)
    guardar_personajes(personajes)

    return jsonify({"status": "ok", "enemigo": nuevo})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)