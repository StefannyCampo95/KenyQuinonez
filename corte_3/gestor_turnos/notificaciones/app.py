import os
from flask import Flask, request, jsonify # type: ignore
import time
from datetime import datetime
import mysql.connector # type: ignore

app = Flask(__name__)

# =========================
# MYSQL
# =========================

def get_connection():

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

conexion = get_connection()

cursor = conexion.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS notificaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    telefono VARCHAR(20),
    mensaje TEXT,
    fecha DATETIME
)
""")

conexion.commit()

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

    return {
        "status": "ok",
        "service": "notificaciones"
    }

# =========================
# ENVIAR NOTIFICACION
# =========================

@app.route("/notificacion", methods=["POST"])
def notificacion():

    global peticiones

    peticiones += 1

    try:

        data = request.json

        telefono = str(data["telefono"])
        mensaje = str(data["mensaje"])

        fecha = datetime.now()

        cursor.execute("""
            INSERT INTO notificaciones
            (telefono, mensaje, fecha)
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

        return jsonify({
            "mensaje": "Notificacion enviada"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# =========================
# LISTAR NOTIFICACIONES
# =========================

@app.route("/listar_notificaciones")
def listar_notificaciones():

    cursor.execute("SELECT * FROM notificaciones")

    resultados = cursor.fetchall()

    notificaciones = []

    for notificacion in resultados:

        notificaciones.append({
            "id": notificacion[0],
            "telefono": notificacion[1],
            "mensaje": notificacion[2]
        })

    return jsonify({
        "notificaciones": notificaciones
    })

# =========================

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)