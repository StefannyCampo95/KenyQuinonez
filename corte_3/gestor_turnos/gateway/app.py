from flask import Flask, request, jsonify  # type: ignore
import requests  # type: ignore
import time

app = Flask(__name__)


@app.route("/")
def home():
    return "API FUNCIONANDO"


# VARIABLES


peticiones = 0
errores = 0


#  CIRCUIT BREAKER


LIMITE_FALLOS = 3
TIEMPO_RECUPERACION = 6
TIMEOUT = 3

circuitos = {

    "usuarios": {
        "fallos": 0,
        "abierto": False,
        "half_open": False,
        "tiempo_respuesta": 0
    },

    "turnos": {
        "fallos": 0,
        "abierto": False,
        "half_open": False,
        "tiempo_respuesta": 0
    },

    "notificaciones": {
        "fallos": 0,
        "abierto": False,
        "half_open": False,
        "tiempo_respuesta": 0
    },

    "historial": {
        "fallos": 0,
        "abierto": False,
        "half_open": False,
        "tiempo_respuesta": 0
    }
}



def circuito_disponible(servicio):

    circuito = circuitos[servicio]

    if circuito["abierto"]:

        tiempo_actual = time.time()

        if (
            tiempo_actual -
            circuito["tiempo_respuesta"]
        ) > TIEMPO_RECUPERACION:

            circuito["half_open"] = True

            print(
                f"[CIRCUITO] {servicio} -> HALF OPEN",
                flush=True
            )

            return True

        return False

    return True


def registrar_exito(servicio):

    circuito = circuitos[servicio]

    circuito["fallos"] = 0
    circuito["abierto"] = False
    circuito["half_open"] = False

    print(
        f"[CIRCUITO] {servicio} -> CLOSED",
        flush=True
    )


def registrar_fallo(servicio):

    circuito = circuitos[servicio]

    circuito["fallos"] += 1

    print(
        f"[CIRCUITO] {servicio} fallo #{circuito['fallos']}",
        flush=True
    )

    if circuito["half_open"]:

        circuito["abierto"] = True
        circuito["half_open"] = False
        circuito["tiempo_respuesta"] = time.time()

        print(
            f"[CIRCUITO] {servicio} -> OPEN",
            flush=True
        )

    elif circuito["fallos"] >= LIMITE_FALLOS:

        circuito["abierto"] = True
        circuito["tiempo_respuesta"] = time.time()

        print(
            f"[CIRCUITO] {servicio} -> OPEN",
            flush=True
        )


# HEALTH CHECK


@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "service": "gateway"
    })


# METRICAS


@app.route("/metricas")
def metricas():

     return jsonify({
        "service": "gateway",
        "peticiones": peticiones,
        "errores": errores,
        "circuitos": circuitos
    })


# CREAR USUARIO


@app.route("/crear_usuario", methods=["POST"])
def crear_usuario():

    global peticiones
    global errores

    peticiones += 1

    if not circuito_disponible("usuarios"):

        return jsonify({
            "error": "Servicio usuarios bloqueado temporalmente"
        }), 503

    inicio = time.time()

    try:

        response = requests.post(
            "http://usuarios:5000/crear_usuario",
            json=request.json,
            timeout=TIMEOUT
        )

        registrar_exito("usuarios")

        fin = time.time()

        print(
            f"[MONITOREO] Usuarios: {fin - inicio:.2f}s",
            flush=True
        )

        return jsonify(
            response.json()
        ), response.status_code

    except Exception as e:

        errores += 1

        registrar_fallo("usuarios")

        print(
            f"[ERROR GATEWAY USUARIOS] {e}",
            flush=True
        )

        return jsonify({
            "error": "Servicio usuarios no disponible"
        }), 500


# LISTAR USUARIOS


@app.route("/listar_usuarios")
def listar_usuarios():

    if not circuito_disponible("usuarios"):

        return jsonify({
            "error": "Servicio usuarios bloqueado temporalmente"
        }), 503

    try:

        response = requests.get(
            "http://usuarios:5000/listar_usuarios",
            timeout=TIMEOUT
        )

        registrar_exito("usuarios")

        return jsonify(response.json())

    except Exception as e:

        registrar_fallo("usuarios")

        print(
            f"[ERROR GATEWAY USUARIOS] {e}",
            flush=True
        )

        return jsonify({
            "error": "Error obteniendo usuarios"
        }), 500


# CREAR TURNO


@app.route("/crear_turno", methods=["POST"])
def crear_turno():

    global peticiones
    global errores

    peticiones += 1

    if not circuito_disponible("turnos"):

        return jsonify({
            "error": "Servicio turnos bloqueado temporalmente"
        }), 503

    inicio = time.time()

    try:

        response = requests.post(
            "http://turnos:5000/crear_turno",
            json=request.json,
            timeout=TIMEOUT
        )

        registrar_exito("turnos")

        fin = time.time()

        print(
            f"[MONITOREO] Turnos: {fin - inicio:.2f}s",
            flush=True
        )

        return jsonify(
            response.json()
        ), response.status_code

    except Exception as e:

        errores += 1

        registrar_fallo("turnos")

        print(
            f"[ERROR GATEWAY TURNOS] {e}",
            flush=True
        )

        return jsonify({
            "error": "Servicio turnos no disponible"
        }), 500


# LISTAR TURNOS


@app.route("/listar_turnos")
def listar_turnos():

    if not circuito_disponible("turnos"):

        return jsonify({
            "error": "Servicio turnos bloqueado temporalmente"
        }), 503

    try:

        response = requests.get(
            "http://turnos:5000/listar_turnos",
            timeout=TIMEOUT
        )

        registrar_exito("turnos")

        return jsonify(response.json())

    except Exception as e:

        registrar_fallo("turnos")

        print(
            f"[ERROR GATEWAY TURNOS] {e}",
            flush=True
        )

        return jsonify({
            "error": "Error obteniendo turnos"
        }), 500
    
    
#NOTIFICACIONES

@app.route("/notificacion", methods=["POST"])
def notificacion():
    global peticiones, errores
    peticiones += 1

    inicio = time.time()

    try:
        response = requests.post(
            "http://notificaciones:5000/notificacion",
            json=request.json
        )

        fin = time.time()

        print(f"[MONITOREO] Tiempo notificaciones: {fin - inicio:.2f}s", flush=True)

        return jsonify(response.json()), response.status_code

    except Exception as e:
        errores += 1
        print(f"[ERROR GATEWAY NOTIFICACIONES] {e}", flush=True)

        return jsonify({
            "error": "Error conectando con notificaciones"
        }), 500


# LISTAR NOTIFICACIONES


@app.route("/listar_notificaciones")
def listar_notificaciones():

    if not circuito_disponible("notificaciones"):

        return jsonify({
            "error": "Servicio notificaciones bloqueado temporalmente"
        }), 503

    try:

        response = requests.get(
            "http://notificaciones:5000/listar_notificaciones",
            timeout=TIMEOUT
        )

        registrar_exito("notificaciones")

        return jsonify(response.json())

    except Exception as e:

        registrar_fallo("notificaciones")

        print(
            f"[ERROR GATEWAY NOTIFICACIONES] {e}",
            flush=True
        )

        return jsonify({
            "error": "Error obteniendo notificaciones"
        }), 500


# HISTORIAL


@app.route("/historial")
def historial():

    if not circuito_disponible("historial"):

        return jsonify({
            "error": "Servicio historial bloqueado temporalmente"
        }), 503

    try:

        response = requests.get(
            "http://historial:5000/listar_historial",
            timeout=TIMEOUT
        )

        registrar_exito("historial")

        return jsonify(response.json())

    except Exception as e:

        registrar_fallo("historial")

        print(
            f"[ERROR GATEWAY HISTORIAL] {e}",
            flush=True
        )

        return jsonify({
            "error": "Error obteniendo historial"
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)