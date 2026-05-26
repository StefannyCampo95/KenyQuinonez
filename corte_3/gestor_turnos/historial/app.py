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
CREATE TABLE IF NOT EXISTS historial (

    id INT AUTO_INCREMENT PRIMARY KEY,
    evento TEXT,
    fecha DATETIME

)
""")

conexion.commit()

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

    cursor.execute("SELECT COUNT(*) AS total FROM historial")

    total = cursor.fetchone()["total"]

    return {
        "peticiones": peticiones,
        "errores": errores,
        "eventos_registrados": total
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

        evento = str(data["evento"])

        fecha = datetime.now()

        # =========================
        # GUARDAR EN MYSQL
        # =========================

        cursor.execute("""
        INSERT INTO historial
        (evento, fecha)
        VALUES (%s, %s)
        """, (
            evento,
            fecha
        ))

        conexion.commit()

        print(
            "[HISTORIAL] Evento registrado",
            flush=True
        )

        fin = time.time()

        print(
            f"[MONITOREO] Tiempo respuesta historial: {fin - inicio:.2f}",
            flush=True
        )

        return jsonify({
            "mensaje": "Evento registrado",
            "evento": {
                "evento": evento,
                "fecha": fecha.strftime("%Y-%m-%d %H:%M:%S")
            }
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

    cursor.execute("""
    SELECT * FROM historial
    ORDER BY id DESC
    """)

    historial = cursor.fetchall()

    return jsonify({
        "historial": historial
    })

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)