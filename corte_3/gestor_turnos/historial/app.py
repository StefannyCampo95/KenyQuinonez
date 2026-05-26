from flask import Flask, request, jsonify # type: ignore
from datetime import datetime
import mysql.connector # type: ignore # type: 
import os

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
CREATE TABLE IF NOT EXISTS historial (
    id INT AUTO_INCREMENT PRIMARY KEY,
    evento TEXT,
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
        "service": "historial"
    }

# =========================
# GUARDAR EVENTO
# =========================

@app.route("/guardar_evento", methods=["POST"])
def guardar_evento():

    global peticiones

    peticiones += 1

    try:

        data = request.json

        evento = data["evento"]

        fecha = datetime.now()

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

        return jsonify({
            "mensaje": "Evento registrado"
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500

# =========================
# LISTAR HISTORIAL
# =========================

@app.route("/listar_historial")
def listar_historial():

    cursor.execute("SELECT * FROM historial")

    resultados = cursor.fetchall()

    historial = []

    for evento in resultados:

        historial.append({
            "id": evento[0],
            "evento": evento[1],
            "fecha": evento[2]
        })

    return jsonify({
        "historial": historial
    })

# =========================

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)