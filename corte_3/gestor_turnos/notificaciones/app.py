import os
from flask import Flask, request, jsonify  # type: ignore
import time
from datetime import datetime
import mysql.connector  # type: ignore

app = Flask(__name__)



def get_connection():

    return mysql.connector.connect(
        host=os.getenv("NOTIFICACIONES_DB_HOST"),
        user=os.getenv("NOTIFICACIONES_DB_USER"),
        password=os.getenv("NOTIFICACIONES_DB_PASSWORD"),
        database=os.getenv("NOTIFICACIONES_DB_NAME")
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


# VARIABLES


peticiones = 0
errores = 0


# HEALTH CHECK


@app.route("/health")
def health():
    return {
        "status": "ok",
        "service": "notificaciones"
    }


# METRICAS


@app.route("/metricas")
def metricas():
    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute("SELECT COUNT(*) FROM notificaciones")
    total = cursor.fetchone()[0]

    cursor.close()
    conexion.close()

    return {
        "peticiones": peticiones,
        "errores": errores,
        "notificaciones_enviadas": total
    }


# REGISTRAR NOTIFICACION 


@app.route("/notificacion", methods=["POST"])
def notificacion():
    global peticiones, errores

    peticiones += 1
    inicio = time.time()

    try:
        data = request.json

        
        # VALIDACION BODY
        
        if not data or "telefono" not in data or "mensaje" not in data:
            errores += 1
            return jsonify({
                "error": "telefono y mensaje son obligatorios"
            }), 400

        telefono = str(data["telefono"])
        mensaje = str(data["mensaje"])

        
        # VALIDACION TELEFONO
        
        if not telefono.isdigit():
            errores += 1
            return jsonify({
                "error": "El telefono solo debe contener numeros"
            }), 400

        if len(telefono) != 10:
            errores += 1
            return jsonify({
                "error": "El telefono debe tener 10 digitos"
            }), 400

        fecha = datetime.now()

        
        # GUARDAR EN LA BD (SIN ENVIO REAL DE SMS)
        
        conexion = get_connection()
        cursor = conexion.cursor()

        cursor.execute("""
            INSERT INTO notificaciones (telefono, mensaje, fecha)
            VALUES (%s, %s, %s)
        """, (telefono, mensaje, fecha))

        conexion.commit()
        cursor.close()
        conexion.close()

        fin = time.time()

        print(f"[NOTIFICACION] Registrada para {telefono}", flush=True)
        print(f"[TIEMPO] {fin - inicio:.2f}s", flush=True)

        return jsonify({
            "mensaje": "Notificacion registrada (sin envio SMS)"
        })

    except Exception as e:
        errores += 1
        print(f"[ERROR NOTIFICACIONES] {e}", flush=True)

        return jsonify({
            "error": str(e)
        }), 500


# LISTAR NOTIFICACIONES


@app.route("/listar_notificaciones")
def listar_notificaciones():
    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute("""
        SELECT id, telefono, mensaje, fecha
        FROM notificaciones
        ORDER BY id DESC
    """)

    resultados = cursor.fetchall()

    cursor.close()
    conexion.close()

    return jsonify({
        "notificaciones": [
            {
                "id": r[0],
                "telefono": r[1],
                "mensaje": r[2],
                "fecha": str(r[3])
            }
            for r in resultados
        ]
    })



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)