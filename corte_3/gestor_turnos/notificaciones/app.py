from flask import Flask, request, jsonify # type: ignore
import time
import random
from datetime import datetime
import mysql.connector # type: ignore

app = Flask(__name__)

# =========================
# VARIABLES
# =========================

notificaciones = []
peticiones = 0
errores = 0

# =========================
# HEALTH CHECK
# =========================

@app.route("/health")
def health():

    print(
        "[HEALTH] Servicio notificaciones activo",
        flush=True
    )

    return {
        "status": "ok",
        "service": "notificaciones"
    }

# =========================
# METRICAS
# =========================

@app.route("/metricas")
def metricas():

    return {
        "peticiones": peticiones,
        "errores": errores,
        "notificaciones_enviadas": len(notificaciones)
    }

# =========================
# ENVIAR NOTIFICACION
# =========================

@app.route("/notificacion", methods=["POST"])
def notificacion():

    global peticiones
    global errores

    peticiones += 1

    inicio = time.time()

    try:

        data = request.json

        # =========================
        # VALIDAR BODY
        # =========================

        if (
            not data
            or "telefono" not in data
            or "mensaje" not in data
        ):

            errores += 1

            return jsonify({
                "error": "Telefono y mensaje son obligatorios"
            }), 400

        telefono = str(data["telefono"])

        # =========================
        # VALIDAR TELEFONO
        # =========================

        if not telefono.isdigit():

            errores += 1

            return jsonify({
                "error": "El telefono solo debe contener numeros"
            }), 400

        # =========================
        # VALIDAR LONGITUD
        # =========================

        if len(telefono) != 10:

            errores += 1

            return jsonify({
                "error": "El telefono debe tener 10 digitos"
            }), 400

       
        # =========================
        # GUARDAR NOTIFICACION
        # =========================

        nueva_notificacion = {
            "telefono": telefono,
            "mensaje": data["mensaje"],
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        notificaciones.append(nueva_notificacion)

        print(
            f"[NOTIFICACION] SMS enviado a {telefono}",
            flush=True
        )

        fin = time.time()

        print(
            f"[MONITOREO] Tiempo respuesta notificaciones: {fin - inicio:.2f}",
            flush=True
        )

        return jsonify({
            "mensaje": "Notificacion enviada",
            "notificacion": nueva_notificacion
        })

    except Exception as e:

        errores += 1

        print(
            f"[ERROR NOTIFICACIONES] {e}",
            flush=True
        )

        return jsonify({
            "error": str(e)
        }), 500

# =========================
# LISTAR NOTIFICACIONES
# =========================

@app.route("/listar_notificaciones")
def listar_notificaciones():

    print(
        "[NOTIFICACIONES] Consultando notificaciones",
        flush=True
    )

    return jsonify({
        "notificaciones": notificaciones
    })

# =========================

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)