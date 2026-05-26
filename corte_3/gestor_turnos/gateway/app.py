from flask import Flask, request, jsonify  # type: ignore
import requests  # type: ignore
import time

app = Flask(__name__)

# =========================
# VARIABLES
# =========================

peticiones = 0
errores = 0

# =========================
# HEALTH CHECK
# =========================

@app.route("/health")
def health():
    print("[HEALTH] Gateway activo", flush=True)
    return {
        "status": "ok",
        "service": "gateway"
    }

# =========================
# METRICAS
# =========================

@app.route("/metricas")
def metricas():
    return {
        "peticiones": peticiones,
        "errores": errores
    }

# =========================
# USUARIOS
# =========================

@app.route("/crear_usuario", methods=["POST"])
def crear_usuario():
    global peticiones, errores
    peticiones += 1

    inicio = time.time()

    try:
        response = requests.post(
            "http://usuarios:5000/crear_usuario",
            json=request.json
        )

        fin = time.time()

        print(f"[MONITOREO] Tiempo usuarios: {fin - inicio:.2f}s", flush=True)

        return jsonify(response.json()), response.status_code

    except Exception as e:
        errores += 1
        print(f"[ERROR GATEWAY USUARIOS] {e}", flush=True)

        return jsonify({"error": "Error conectando con usuarios"}), 500


@app.route("/listar_usuarios")
def listar_usuarios():

    try:
        response = requests.get("http://usuarios:5000/listar_usuarios")
        return jsonify(response.json())

    except Exception as e:
        print(f"[ERROR GATEWAY USUARIOS] {e}", flush=True)
        return jsonify({"error": "Error obteniendo usuarios"}), 500

# =========================
# TURNOS
# =========================

@app.route("/turno", methods=["POST"])
def crear_turno():
    global peticiones, errores
    peticiones += 1

    inicio = time.time()

    try:
        response = requests.post(
            "http://turnos:5000/turno",
            json=request.json
        )

        fin = time.time()

        print(f"[MONITOREO] Tiempo turnos: {fin - inicio:.2f}s", flush=True)

        return jsonify(response.json()), response.status_code

    except Exception as e:
        errores += 1
        print(f"[ERROR GATEWAY TURNOS] {e}", flush=True)

        return jsonify({"error": "Error conectando con turnos"}), 500


@app.route("/listar_turnos")
def listar_turnos():

    try:
        response = requests.get("http://turnos:5000/listar_turnos")
        return jsonify(response.json())

    except Exception as e:
        print(f"[ERROR GATEWAY TURNOS] {e}", flush=True)
        return jsonify({"error": "Error obteniendo turnos"}), 500


# NOTIFICACIONES


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


@app.route("/listar_notificaciones")
def listar_notificaciones():

    try:
        response = requests.get("http://notificaciones:5000/listar_notificaciones")
        return jsonify(response.json())

    except Exception as e:
        print(f"[ERROR GATEWAY NOTIFICACIONES] {e}", flush=True)
        return jsonify({"error": "Error obteniendo notificaciones"}), 500

# =========================
# HISTORIAL
# =========================

@app.route("/historial")
def historial():

    try:
        response = requests.get("http://historial:5000/listar_historial")
        return jsonify(response.json())

    except Exception as e:
        print(f"[ERROR GATEWAY HISTORIAL] {e}", flush=True)
        return jsonify({"error": "Error obteniendo historial"}), 500


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)