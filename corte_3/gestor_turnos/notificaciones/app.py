from flask import Flask, request, jsonify # type: ignore
import time
from datetime import datetime
import mysql.connector # type: ignore
import os

app = Flask(__name__)

# =========================
# VARIABLES
# =========================

peticiones = 0
errores = 0

# =========================
# CONEXION MYSQL
# =========================

conexion = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)

cursor = conexion.cursor(dictionary=True)

# =========================
# CREAR TABLA
# =========================

cursor.execute("""
CREATE TABLE IF NOT EXISTS notificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telefono VARCHAR(20),
    mensaje TEXT,
    fecha VARCHAR(50)
)
""")

conexion.commit()

# =========================
# HOME
# =========================

@app.route("/")
def home():

    return {
        "mensaje": "Servicio notificaciones funcionando"
    }

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

    cursor.execute(
        "SELECT COUNT(*) AS total FROM notificaciones"
    )

    total = cursor.fetchone()

    return {
        "peticiones": peticiones,
        "errores": errores,
        "notificaciones_enviadas": total["total"]
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
        mensaje = str(data["mensaje"])

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
        # FECHA
        # =========================

        fecha = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # =========================
        # INSERTAR NOTIFICACION
        # =========================

        cursor.execute("""
        INSERT INTO notificaciones (
            telefono,
            mensaje,
            fecha
        )
        VALUES (%s, %s, %s)
        """, (
            telefono,
            mensaje,
            fecha
        ))

        conexion.commit()

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
            "notificacion": {
                "telefono": telefono,
                "mensaje": mensaje,
                "fecha": fecha
            }
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

    global peticiones

    peticiones += 1

    print(
        "[NOTIFICACIONES] Consultando notificaciones",
        flush=True
    )

    cursor.execute(
        "SELECT * FROM notificaciones"
    )

    notificaciones = cursor.fetchall()

    return jsonify({
        "notificaciones": notificaciones
    })


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)