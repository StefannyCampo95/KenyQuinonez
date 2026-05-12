from flask import Flask, request, jsonify # type: ignore
import requests # type: ignore
import time

app = Flask(__name__)

# Inicializamos los circuitos para cada servicio

circuito = {
    "usuarios": {
        "fallos": 0,
        "abierto": False,
        "half_open": False,
        "ultimo_fallo": 0
    },

    "mascotas": {
        "fallos": 0,
        "abierto": False,
        "half_open": False,
        "ultimo_fallo": 0
    }
}

# Variables globales para los circuitos
LIMITE_FALLOS = 3
TIEMPO_RECUPERACION = 8


@app.route("/usuarios")
def usuarios():

    global circuito

    servicio = circuito["usuarios"]

    #Preguntamos si el circuito está abierto

    if servicio["abierto"]:

        tiempo_actual = time.time()

        # Pasar a half-open después del tiempo de recuperación
        if tiempo_actual - servicio["ultimo_fallo"] > TIEMPO_RECUPERACION:

            servicio["half_open"] = True

            print(
                "Usuarios pasando a HALF-OPEN",
                flush=True
            )

        else:

            return {
                "error": "Servicio usuarios temporalmente bloqueado"
            }, 503

    try:

        response = requests.get(
            "http://usuarios:5000/usuarios",
            timeout=2
        )

        #cerrar circuito si funciona

        servicio["fallos"] = 0
        servicio["abierto"] = False
        servicio["half_open"] = False

        print(
            "Circuito usuarios cerrado",
            flush=True
        )

        return jsonify(response.json())

    except:

        servicio["fallos"] += 1

        print(
            f"Fallo usuarios número {servicio['fallos']}",
            flush=True
        )

        # Si falla en half-open, volver a abrir el circuito

        if servicio["half_open"]:

            servicio["abierto"] = True
            servicio["half_open"] = False
            servicio["ultimo_fallo"] = time.time()

            print(
                "Usuarios volvió a OPEN",
                flush=True
            )

        # Abrir circuito

        elif servicio["fallos"] >= LIMITE_FALLOS:

            servicio["abierto"] = True
            servicio["ultimo_fallo"] = time.time()

            print(
                "Circuito usuarios abierto",
                flush=True
            )

        return {"error": "Servicio usuarios no disponible"}, 503




@app.route("/mascotas")
def mascotas():

    global circuito

    servicio = circuito["mascotas"]

    #Preguntamos si el circuito está abierto

    if servicio["abierto"]:

        tiempo_actual = time.time()

        # Pasar a half-open después del tiempo de recuperación
        if tiempo_actual - servicio["ultimo_fallo"] > TIEMPO_RECUPERACION:

            servicio["half_open"] = True

            print(
                "Mascotas pasando a HALF-OPEN",
                flush=True
            )

        else:

            return {
                "error": "Servicio mascotas temporalmente bloqueado"
            }, 503

    try:

        response = requests.get(
            "http://backend:5000/mascotas",
            timeout=2
        )

        #cerrar circuito si funciona

        servicio["fallos"] = 0
        servicio["abierto"] = False
        servicio["half_open"] = False

        print(
            "Circuito mascotas cerrado",
            flush=True
        )

        return jsonify(response.json())

    except:

        servicio["fallos"] += 1

        print(
            f"Fallo mascotas número {servicio['fallos']}",
            flush=True
        )

        # si falla en half-open, volver a abrir el circuito

        if servicio["half_open"]:

            servicio["abierto"] = True
            servicio["half_open"] = False
            servicio["ultimo_fallo"] = time.time()

            print(
                "Mascotas volvió a OPEN",
                flush=True
            )

        # Abrir circuito

        elif servicio["fallos"] >= LIMITE_FALLOS:

            servicio["abierto"] = True
            servicio["ultimo_fallo"] = time.time()

            print(
                "Circuito mascotas abierto",
                flush=True
            )

        return {"error": "Servicio mascotas no disponible"}, 503



@app.route("/resumen")
def resumen():

    resultado = {}

    # USAMOS LOS CIRCUITOS PARA CONSULTAR AMBOS SERVICIOS

    usuarios_service = circuito["usuarios"]

    if usuarios_service["abierto"]:

        tiempo_actual = time.time()

        if tiempo_actual - usuarios_service["ultimo_fallo"] > TIEMPO_RECUPERACION:

            usuarios_service["half_open"] = True

        else:

            resultado["usuarios"] = "Circuito abierto"

    if not usuarios_service["abierto"] or usuarios_service["half_open"]:

        try:

            response = requests.get(
                "http://usuarios:5000/usuarios",
                timeout=2
            )

            usuarios_service["fallos"] = 0
            usuarios_service["abierto"] = False
            usuarios_service["half_open"] = False

            resultado["usuarios"] = response.json()

        except:

            usuarios_service["fallos"] += 1

            if usuarios_service["half_open"]:

                usuarios_service["abierto"] = True
                usuarios_service["half_open"] = False
                usuarios_service["ultimo_fallo"] = time.time()

            elif usuarios_service["fallos"] >= LIMITE_FALLOS:

                usuarios_service["abierto"] = True
                usuarios_service["ultimo_fallo"] = time.time()

            resultado["usuarios"] = "No disponible"



    mascotas_service = circuito["mascotas"]

    if mascotas_service["abierto"]:

        tiempo_actual = time.time()

        if tiempo_actual - mascotas_service["ultimo_fallo"] > TIEMPO_RECUPERACION:

            mascotas_service["half_open"] = True

        else:

            resultado["mascotas"] = "Circuito abierto"

    if not mascotas_service["abierto"] or mascotas_service["half_open"]:

        try:

            response = requests.get(
                "http://backend:5000/mascotas",
                timeout=2
            )

            mascotas_service["fallos"] = 0
            mascotas_service["abierto"] = False
            mascotas_service["half_open"] = False

            resultado["mascotas"] = response.json()

        except:

            mascotas_service["fallos"] += 1

            if mascotas_service["half_open"]:

                mascotas_service["abierto"] = True
                mascotas_service["half_open"] = False
                mascotas_service["ultimo_fallo"] = time.time()

            elif mascotas_service["fallos"] >= LIMITE_FALLOS:

                mascotas_service["abierto"] = True
                mascotas_service["ultimo_fallo"] = time.time()

            resultado["mascotas"] = "No disponible"

    return jsonify(resultado)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)