from flask import Flask, request, jsonify # type: ignore
import requests # type: ignore
import time
from datetime import datetime
import mysql.connector # type: ignore
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
CREATE TABLE IF NOT EXISTS turnos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    identificacion VARCHAR(20),
    telefono VARCHAR(20),
    turno VARCHAR(20),
    estado VARCHAR(20),
    fecha DATETIME
)
""")

conexion.commit()

# =========================
# VARIABLES
# =========================

contador = 1
peticiones = 0
errores = 0

fallos_notificaciones = 0
circuit_breaker = "CLOSED"

# =========================
# HEALTH CHECK
# =========================

@app.route("/health")
def health():

    return {
        "status": "ok",
        "service": "turnos",
        "circuit_breaker": circuit_breaker
    }

# =========================
# METRICAS
# =========================

@app.route("/metricas")
def metricas():

    return {
        "peticiones": peticiones,
        "errores": errores,
        "estado_circuit_breaker": circuit_breaker
    }

# =========================
# CREAR TURNO
# =========================

@app.route("/turno", methods=["POST"])
def crear_turno():

    global contador
    global peticiones
    global errores
    global fallos_notificaciones
    global circuit_breaker

    peticiones += 1

    inicio = time.time()

    try:

        data = request.json

        identificacion = str(data["identificacion"])
        telefono = str(data["telefono"])

        if not identificacion.isdigit():

            return jsonify({
                "error": "Identificacion invalida"
            }), 400

        if not telefono.isdigit():

            return jsonify({
                "error": "Telefono invalido"
            }), 400

        if len(telefono) != 10:

            return jsonify({
                "error": "El telefono debe tener 10 digitos"
            }), 400

        cursor.execute("""
            SELECT * FROM turnos
            WHERE identificacion = %s
            AND estado = 'pendiente'
        """, (identificacion,))

        turno_existente = cursor.fetchone()

        if turno_existente:

            return jsonify({
                "error": "Usuario ya tiene turno pendiente"
            }), 400

        turno_generado = "T" + str(contador)

        fecha = datetime.now()

        cursor.execute("""
            INSERT INTO turnos
            (identificacion, telefono, turno, estado, fecha)
            VALUES (%s, %s, %s, %s, %s)
        """, (
            identificacion,
            telefono,
            turno_generado,
            "pendiente",
            fecha
        ))

        conexion.commit()

        contador += 1

        print(
            f"[TURNOS] Turno generado: {turno_generado}",
            flush=True
        )

        # =========================
        # CIRCUIT BREAKER
        # =========================

        if circuit_breaker == "OPEN":

            print(
                "[CIRCUIT BREAKER] OPEN",
                flush=True
            )

            time.sleep(5)

            circuit_breaker = "HALF-OPEN"

        try:

            response = requests.post(
                "http://notificaciones:5000/notificacion",
                json={
                    "telefono": telefono,
                    "mensaje": f"Su turno es {turno_generado}"
                },
                timeout=3
            )

            if response.status_code == 200:

                fallos_notificaciones = 0
                circuit_breaker = "CLOSED"

                print(
                    "[NOTIFICACIONES] Enviada correctamente",
                    flush=True
                )

            else:

                fallos_notificaciones += 1

        except Exception as e:

            fallos_notificaciones += 1

            print(
                f"[ERROR NOTIFICACIONES] {e}",
                flush=True
            )

        if fallos_notificaciones >= 3:

            circuit_breaker = "OPEN"

            print(
                "[CIRCUIT BREAKER] OPEN",
                flush=True
            )

        # =========================
        # HISTORIAL
        # =========================

        try:

            requests.post(
                "http://historial:5000/guardar_evento",
                json={
                    "evento": f"Turno generado {turno_generado}"
                }
            )

        except Exception as e:

            print(
                f"[ERROR HISTORIAL] {e}",
                flush=True
            )

        fin = time.time()

        print(
            f"[MONITOREO] Tiempo respuesta turnos: {fin - inicio:.2f}",
            flush=True
        )

        return jsonify({
            "turno": turno_generado,
            "estado": "pendiente"
        })

    except Exception as e:

        errores += 1

        return jsonify({
            "error": str(e)
        }), 500

# =========================
# LISTAR TURNOS
# =========================

@app.route("/listar_turnos")
def listar_turnos():

    cursor.execute("SELECT * FROM turnos")

    resultados = cursor.fetchall()

    turnos = []

    for turno in resultados:

        turnos.append({
            "id": turno[0],
            "identificacion": turno[1],
            "telefono": turno[2],
            "turno": turno[3],
            "estado": turno[4]
        })

    return jsonify({
        "turnos": turnos
    })


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)