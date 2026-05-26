from flask import Flask, request, jsonify # type: ignore
import time
from datetime import datetime
import mysql.connector # type: ignore

app = Flask(__name__)

# =========================
# VARIABLES
# =========================

historial = []
peticiones = 0
errores = 0

# =========================
# HEALTH CHECK
# =========================

@app.route("/health")
def health():

    print(
        "[HEALTH] Servicio historial activo",
        flush=True
    )

    return {
        "status": "ok",
        "service": "historial"
    }

# =========================
# METRICAS
# =========================

@app.route("/metricas")
def metricas():

    return {
        "peticiones": peticiones,
        "errores": errores,
        "eventos_registrados": len(historial)
    }

# =========================
# REGISTRAR EVENTO
# =========================

@app.route("/guardar_evento", methods=["POST"])
def guardar_evento():

    global peticiones
    global errores

    peticiones += 1

    inicio = time.time()

    try:

        data = request.json

        # =========================
        # VALIDAR BODY
        # =========================

        if not data or "evento" not in data:

            errores += 1

            return jsonify({
                "error": "Evento requerido"
            }), 400

        # =========================
        # CREAR EVENTO
        # =========================

        evento = {
            "evento": data["evento"],
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        historial.append(evento)

        print(
            f"[HISTORIAL] Evento registrado",
            flush=True
        )

        fin = time.time()

        print(
            f"[MONITOREO] Tiempo respuesta historial: {fin - inicio:.2f}",
            flush=True
        )

        return jsonify({
            "mensaje": "Evento registrado",
            "evento": evento
        })

    except Exception as e:

        errores += 1

        print(
            f"[ERROR HISTORIAL] {e}",
            flush=True
        )

        return jsonify({
            "error": str(e)
        }), 500

# =========================
# LISTAR HISTORIAL
# =========================

@app.route("/listar_historial")
def listar_historial():

    print(
        "[HISTORIAL] Consultando historial",
        flush=True
    )

    return jsonify({
        "historial": historial
    })

# =========================

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)