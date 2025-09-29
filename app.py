from flask import Flask, render_template, request, jsonify
import json
import threading
import tkinter as tk
from tkinter import ttk

# Flask
app = Flask(__name__)

def cargar_personajes():
    try:
        with open("personajes.json", "r") as f:
            data = json.load(f)
            return data.get("personajes", [])
    except FileNotFoundError:
        return []

def cargar_ronda():
    try:
        with open("personajes.json", "r") as f:
            data = json.load(f)
            return data.get("ronda", 0)
    except FileNotFoundError:
        return 0

def guardar_personajes(personajes):
    try:
        with open("personajes.json", "r") as f:
            data = json.load(f)
            ronda = data.get("ronda", 0) 
    except FileNotFoundError:
        ronda = 0

    with open("personajes.json", "w") as f:
        json.dump({"ronda": ronda, "personajes": personajes}, f, indent=4)


def guardar_ronda(ronda):
    try:
        with open("personajes.json", "r") as f:
            data = json.load(f)
            personajes_actuales = data.get("personajes", [])
    except FileNotFoundError:
        personajes_actuales = []

    with open("personajes.json", "w") as f:
        json.dump({"ronda": ronda, "personajes": personajes_actuales}, f, indent=4)

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
                    else:
                        if estado not in p["estados"]:
                            p["estados"].append(estado)
                        if estado in ["Aturdido", "Inconsciente", "Paralizado"] and "Incapacitado" not in p["estados"]:
                            p["estados"].append("Incapacitado")

                elif accion == "quitar":
                    if estado == "Cansancio":
                        p["estados"] = [s for s in p["estados"] if not s.startswith("Cansancio")]
                    else:
                        if estado in p["estados"]:
                            p["estados"].remove(estado)
                    if estado in ["Aturdido", "Inconsciente", "Paralizado"] and "Incapacitado" in p["estados"]:
                        p["estados"].remove("Incapacitado")

    # Actualizar ronda si se envía
    if "ronda" in data:
        ronda_actual = data["ronda"]

    guardar_personajes(personajes)
    guardar_ronda(ronda_actual)
    return jsonify({"status": "ok"})



@app.route("/dashboard-data")
def dashboard_data():
    global ronda_actual
    personajes = cargar_personajes()
    ronda = cargar_ronda()
    # Ordenar por iniciativa
    personajes_ordenados = sorted(personajes, key=lambda p: p.get("iniciativa", 0), reverse=True)
    return jsonify({
        "ronda": ronda,
        "personajes": personajes_ordenados
    })


# Tkinter
vida_labels = []
vida_vars = []
heridas_vars = []
shock_vars = []
barra_vida = []
estado_labels = []

def actualizar_valores(index):
    p = personajes[index]
    vida_vars[index].set(p["vida_actual"])
    barra_vida[index]["maximum"] = p["vida_max"]  # <-- actualizar máximo
    vida_labels[index]["text"] = f"{p['vida_actual']} / {p['vida_max']} PV"
    heridas_vars[index].set(p["heridas"])
    shock_vars[index].set(p["shock"])
    estado_labels[index]["text"] = ", ".join(p.get("estados", []))

def modificar(index, tipo, cantidad):
    p = personajes[index]
    if tipo == "vida":
        p["vida_actual"] = max(0, min(p["vida_max"], p["vida_actual"] + cantidad))
    elif tipo == "heridas":
        heridas_antes = p["heridas"]
        p["heridas"] = max(0, p["heridas"] + cantidad)

        # Subir heridas: solo aumenta shock si superas 3 heridas
        if cantidad > 0 and p["heridas"] > 3:
            nuevas_heridas = max(0, p["heridas"] - max(3, heridas_antes))
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

    # Variables para seleccionar personaje y estado
    estado_seleccionado = tk.StringVar()
    personaje_seleccionado = tk.StringVar()
    
    # Contador de rondas
    ronda_var = tk.IntVar(value=0)
    ronda_label = ttk.Label(root, text=f"Ronda: {ronda_var.get()}", font=("Arial", 14, "bold"))
    ronda_label.grid(row=100, column=0, columnspan=2, pady=10, sticky="w")
    
    # Lista de estados posibles
    estados_disponibles = [
        "Agarrado","Apresado","Asustado","Aturdido","Cansancio",
        "Cegado","Derribado","Ensordecido","Envenenado","Hechizado",
        "Incapacitado","Inconsciente","Invisible","Paralizado","Petrificado"
    ]

    # Combobox de selección de personaje
    ttk.Label(root, text="Personaje:").grid(row=101, column=0, sticky="w")
    personaje_menu = ttk.Combobox(root, values=[p["nombre"] for p in personajes], textvariable=personaje_seleccionado, state="readonly")
    personaje_menu.grid(row=101, column=0, sticky="w", padx=70)

    # Combobox de selección de estado
    ttk.Label(root, text="Estado:").grid(row=102, column=0, sticky="w")
    estado_menu = ttk.Combobox(root, values=estados_disponibles, textvariable=estado_seleccionado, state="readonly")
    estado_menu.grid(row=102, column=0, sticky="w", padx=70)

    # Botón para agregar estado
    def agregar_estado():
        nombre = personaje_seleccionado.get()
        estado = estado_seleccionado.get()
        if not nombre or not estado:
            return
        for p in personajes:
            if p["nombre"] == nombre:
                if "estados" not in p:
                    p["estados"] = []

                # Reglas especiales para Cansancio
                if estado == "Cansancio":
                    niveles = [s for s in p["estados"] if s.startswith("Cansancio")]
                    if niveles:
                        # Tomar el nivel más alto y subirlo
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
                        # No hay ninguno, crear el primero
                        p["estados"].append("Cansancio")
                else:
                    # Agregar otros estados normales si no están ya
                    if estado not in p["estados"]:
                        p["estados"].append(estado)

                    # Estados que obligan a Incapacitado
                    if estado in ["Aturdido", "Inconsciente", "Paralizado"] and "Incapacitado" not in p["estados"]:
                        p["estados"].append("Incapacitado")

                guardar_personajes(personajes)
                actualizar_valores(personajes.index(p))
                break
    ttk.Button(root, text="Agregar estado", command=agregar_estado).grid(row=101, column=0, columnspan=2, padx=100)

    # Botón para quitar estado
    def quitar_estado():
        nombre = personaje_seleccionado.get()
        estado = estado_seleccionado.get()
        if not nombre or not estado:
            return
        for p in personajes:
            if p["nombre"] == nombre and "estados" in p:
                # Manejo especial de Cansancio: eliminar todos los niveles
                if estado == "Cansancio":
                    p["estados"] = [s for s in p["estados"] if not s.startswith("Cansancio")]
                else:
                    # Quitar estado normal si existe
                    if estado in p["estados"]:
                        p["estados"].remove(estado)
                
                # Reglas especiales al quitar ciertos estados que generan Incapacitado
                if estado in ["Aturdido", "Inconsciente", "Paralizado"] and "Incapacitado" in p["estados"]:
                    p["estados"].remove("Incapacitado")
                
                guardar_personajes(personajes)
                actualizar_valores(personajes.index(p))
                break
    ttk.Button(root, text="Quitar estado", command=quitar_estado).grid(row=102, column=0, columnspan=2, padx=100)


    # Variables para turno
    turno_indices = sorted(range(len(personajes)), key=lambda i: personajes[i].get("iniciativa", 0), reverse=True)
    turno_actual = 0
    nombre_labels = []

    frames = []
    # Crear los frames de cada personaje
    for i, p in enumerate(personajes):
        frame = ttk.Frame(root, padding=10)
        frame.grid(row=i//3, column=i%3, padx=10, pady=10)
        frames.append(frame)

        lbl_nombre = ttk.Label(frame, text=p["nombre"], font=("Arial", 14, "bold"), foreground="white")
        lbl_nombre.grid(row=0, column=0, columnspan=2)
        nombre_labels.append(lbl_nombre)

        # Barra de vida
        ttk.Label(frame, text="Vida:").grid(row=1, column=0, sticky="w")
        vida_var = tk.IntVar(value=p["vida_actual"])
        vida_vars.append(vida_var)
        barra = ttk.Progressbar(frame, maximum=p["vida_max"], length=150, variable=vida_var)
        barra.grid(row=1, column=1, columnspan=2)
        barra_vida.append(barra)
        vida_label = tk.Label(frame, text=f"{p['vida_actual']} / {p['vida_max']} PV")
        vida_label.grid(row=2, column=0, columnspan=3, sticky="w")
        vida_labels.append(vida_label)

        # Entrada para modificar vida actual
        vida_input = tk.StringVar(value="0")
        ttk.Entry(frame, width=5, textvariable=vida_input).grid(row=3, column=0)
        ttk.Button(frame, text="Aplicar", width=6, command=lambda i=i, v=vida_input: modificar(i, "vida", int(v.get()) if v.get().lstrip("-").isdigit() else 0)).grid(row=3, column=1)

        # Entrada para modificar vida máxima
        vida_max_input = tk.StringVar(value=str(p["vida_max"]))
        ttk.Entry(frame, width=5, textvariable=vida_max_input).grid(row=3, column=2)
        def aplicar_vida_max(i=i, v_max=vida_max_input):
            try:
                nuevo_max = int(v_max.get())
                if nuevo_max < 1:
                    return
                personajes[i]["vida_max"] = nuevo_max
                # Ajustar vida actual si supera el nuevo máximo
                if personajes[i]["vida_actual"] > nuevo_max:
                    personajes[i]["vida_actual"] = nuevo_max
                # Actualizar barra de vida
                barra_vida[i]["maximum"] = nuevo_max
                actualizar_valores(i)
                guardar_personajes(personajes)
            except ValueError:
                pass
        ttk.Button(frame, text="V.Max", width=10, command=aplicar_vida_max).grid(row=3, column=3)

        # Botones +1/-1 para vida
        ttk.Button(frame, text="+", width=3, command=lambda i=i: modificar(i, "vida", 1)).grid(row=4, column=0)
        ttk.Button(frame, text="-", width=3, command=lambda i=i: modificar(i, "vida", -1)).grid(row=4, column=1)

        # Heridas
        ttk.Label(frame, text="Heridas:").grid(row=5, column=0, sticky="w")
        heridas_var = tk.IntVar(value=p["heridas"])
        heridas_vars.append(heridas_var)
        ttk.Label(frame, textvariable=heridas_var).grid(row=5, column=1, sticky="w")
        ttk.Button(frame, text="+", width=3, command=lambda i=i: modificar(i,"heridas",1)).grid(row=6, column=0)
        ttk.Button(frame, text="-", width=3, command=lambda i=i: modificar(i,"heridas",-1)).grid(row=6, column=1)

        # Shock
        ttk.Label(frame, text="Shock:").grid(row=7, column=0, sticky="w")
        shock_var = tk.IntVar(value=p["shock"])
        shock_vars.append(shock_var)
        ttk.Label(frame, textvariable=shock_var).grid(row=7, column=1, sticky="w")
        ttk.Button(frame, text="+", width=3, command=lambda i=i: modificar(i,"shock",1)).grid(row=8, column=0)
        ttk.Button(frame, text="-", width=3, command=lambda i=i: modificar(i,"shock",-1)).grid(row=8, column=1)


        # Iniciativa
        ttk.Label(frame, text="Inic.:").grid(row=9, column=0, sticky="w", padx=5)
        iniciativa_var = tk.StringVar(value=str(p.get("iniciativa", 0)))
        ttk.Entry(frame, width=5, textvariable=iniciativa_var).grid(row=9, column=1)
        
        def aplicar_iniciativa(i=i, v_inic=iniciativa_var):
            try:
                nuevo_valor = int(v_inic.get())
                personajes[i]["iniciativa"] = nuevo_valor
                guardar_personajes(personajes)
                actualizar_valores(i)
            except ValueError:
                pass
        ttk.Button(frame, text="Aplicar", width=6, command=aplicar_iniciativa).grid(row=9, column=2)

        # Label de estados
        lbl_estados = tk.Label(frame, text=", ".join(p.get("estados", [])), wraplength=180, justify="left")
        lbl_estados.grid(row=10, column=0, columnspan=3, sticky="w")
        estado_labels.append(lbl_estados)


    # Modificar actualizar_valores para actualizar los estados
    def actualizar_valores(index):
        p = personajes[index]
        vida_vars[index].set(p["vida_actual"])
        heridas_vars[index].set(p["heridas"])
        shock_vars[index].set(p["shock"])
        barra_vida[index]["value"] = p["vida_actual"]
        vida_labels[index]["text"] = f"{p['vida_actual']} / {p['vida_max']} PV"
        estado_labels[index]["text"] = ", ".join(p.get("estados", []))
        

    def actualizar_turnos():
        for i, p in enumerate(personajes):
            if p.get("turno"):
                nombre_labels[i].configure(foreground="#C0C000")  # color turno
            else:
                nombre_labels[i].configure(foreground="black")   # color normal

    def pasar_turno():
        nonlocal turno_actual
        for p in personajes:
            p["turno"] = False
        idx = turno_indices[turno_actual]
        personajes[idx]["turno"] = True
        actualizar_turnos()

        # si volvemos al primero : nueva ronda
        if turno_actual == 0:
            ronda_actual = cargar_ronda()
            ronda_actual += 1
            ronda_var.set(ronda_actual)
            ronda_label.config(text=f"Ronda: {ronda_var.get()}")
            guardar_ronda(ronda_actual)
        
        # avanzar turno
        turno_actual = (turno_actual + 1) % len(turno_indices)

        guardar_personajes(personajes)




    # Botón pasar turno
    ttk.Button(root, text="Pasar turno", command=pasar_turno).grid(row=102, column=1, columnspan=2, pady=5)

    pasar_turno()  # Iniciar el primer turno
    root.mainloop()


# Ejecutar Flask en un hilo
flask_thread = threading.Thread(target=lambda: app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False))
flask_thread.daemon = True
flask_thread.start()

# Ejecutar Tkinter en el hilo principal
run_tkinter()