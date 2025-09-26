from flask import Flask, render_template, request, jsonify
import json
import threading
import tkinter as tk
from tkinter import ttk

# --- Flask ---
app = Flask(__name__)

def cargar_personajes():
    try:
        with open("personajes.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def guardar_personajes(personajes):
    with open("personajes.json", "w") as f:
        json.dump(personajes, f, indent=4)

@app.route("/dashboard")
def dashboard():
    personajes = cargar_personajes()
    return render_template("dashboard.html", personajes=personajes)

@app.route("/actualizar", methods=["POST"])
def actualizar():
    data = request.json
    personajes = cargar_personajes()
    for p in personajes:
        if p["nombre"] == data["nombre"]:
            p["vida_actual"] = max(0, min(p["vida_max"], data.get("vida_actual", p["vida_actual"])))
            p["heridas"] = data.get("heridas", p["heridas"])
            p["shock"] = max(p["heridas"]-4, 0)
    guardar_personajes(personajes)
    return jsonify({"status": "ok"})

@app.route("/dashboard-data")
def dashboard_data():
    personajes = cargar_personajes()
    return jsonify({"personajes": personajes})

# --- Tkinter ---
vida_labels = []
vida_vars = []
heridas_vars = []
shock_vars = []
barra_vida = []

def actualizar_valores(index):
    p = personajes[index]
    vida_vars[index].set(p["vida_actual"])
    heridas_vars[index].set(p["heridas"])
    shock_vars[index].set(p["shock"])
    barra_vida[index]["value"] = p["vida_actual"]
    vida_labels[index]["text"] = f"{p['vida_actual']} / {p['vida_max']} PV"

def modificar(index, tipo, cantidad):
    p = personajes[index]
    if tipo == "vida":
        p["vida_actual"] = max(0, min(p["vida_max"], p["vida_actual"] + cantidad))
    elif tipo == "heridas":
        heridas_antes = p["heridas"]
        p["heridas"] = max(0, p["heridas"] + cantidad)

        # Subir heridas: solo aumenta shock si superas 4 heridas
        if cantidad > 0 and p["heridas"] > 3:
            nuevas_heridas = max(0, p["heridas"] - max(4, heridas_antes))
            if nuevas_heridas > 0:
                p["shock"] = min(3, p["shock"] + nuevas_heridas)

        # Bajar heridas por debajo de 4 resetea shock
        if p["heridas"] < 4:
            p["shock"] = 0

    elif tipo == "shock":
        p["shock"] = max(0, min(3, p["shock"] + cantidad))

    actualizar_valores(index)
    guardar_personajes(personajes)

personajes = cargar_personajes()

def run_tkinter():
    root = tk.Tk()
    root.title("Control DnD")

    for i, p in enumerate(personajes):
        frame = ttk.Frame(root, padding=10)
        frame.grid(row=i//2, column=i%2, padx=10, pady=10)

        ttk.Label(frame, text=p["nombre"], font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2)

        # Barra de vida
        ttk.Label(frame, text="Vida:").grid(row=1, column=0, sticky="w")
        vida_var = tk.IntVar(value=p["vida_actual"])
        vida_vars.append(vida_var)
        barra = ttk.Progressbar(frame, maximum=p["vida_max"], length=150, variable=vida_var)
        barra.grid(row=1, column=1)
        barra_vida.append(barra)
        vida_label = tk.Label(frame, text=f"{p['vida_actual']} / {p['vida_max']} PV")
        vida_label.grid(row=1, column=2, sticky="w")
        vida_labels.append(vida_label)

        # Botones de vida
        ttk.Button(frame, text="+", width=3, command=lambda i=i: modificar(i,"vida",1)).grid(row=2, column=0)
        ttk.Button(frame, text="-", width=3, command=lambda i=i: modificar(i,"vida",-1)).grid(row=2, column=1)

        # Heridas
        ttk.Label(frame, text="Heridas:").grid(row=3, column=0, sticky="w")
        heridas_var = tk.IntVar(value=p["heridas"])
        heridas_vars.append(heridas_var)
        ttk.Label(frame, textvariable=heridas_var).grid(row=3, column=1, sticky="w")
        ttk.Button(frame, text="+", width=3, command=lambda i=i: modificar(i,"heridas",1)).grid(row=4, column=0)
        ttk.Button(frame, text="-", width=3, command=lambda i=i: modificar(i,"heridas",-1)).grid(row=4, column=1)

        # Shock
        ttk.Label(frame, text="Shock:").grid(row=5, column=0, sticky="w")
        shock_var = tk.IntVar(value=p["shock"])
        shock_vars.append(shock_var)
        ttk.Label(frame, textvariable=shock_var).grid(row=5, column=1, sticky="w")
        ttk.Button(frame, text="+", width=3, command=lambda i=i: modificar(i,"shock",1)).grid(row=6, column=0)
        ttk.Button(frame, text="-", width=3, command=lambda i=i: modificar(i,"shock",-1)).grid(row=6, column=1)

    root.mainloop()

# --- Ejecutar Flask en un hilo ---
flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False))
flask_thread.daemon = True
flask_thread.start()

# Ejecutar Tkinter en el hilo principal
run_tkinter()
