from flask import Flask, request, jsonify # type: ignore
import requests # type: ignore
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
# CIRCUIT BREAKER
# =========================

fallos_notificaciones = 0
circuit_breaker = "CLOSED"

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
CREATE TABLE IF NOT EXISTS turnos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    identificacion VARCHAR(50),
    telefono VARCHAR(20),
    turno VARCHAR(20),
    estado VARCHAR(20),
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
        "mensaje": "Servicio turnos funcionando"
    }

# =========================
# HEALTH CHECK
# =========================

@app.route("/health")
def health():

    print(
        "[HEALTH] Servicio turnos activo",
        flush=True
    )

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

    cursor.execute("SELECT COUNT(*) AS total FROM turnos")

    total = cursor.fetchone()

    return {
        "peticiones": peticiones,
        "errores": errores,
        "turnos_generados": total["total"],
        "estado_circuit_breaker": circuit_breaker
    }

# =========================
# CREAR TURNO
# =========================

@app.route("/turno", methods=["POST"])
def crear_turno():

    global peticiones
    global errores
    global fallos_notificaciones
    global circuit_breaker

    peticiones += 1

    inicio = time.time()

    try:

        data = request.json

        # =========================
        # VALIDAR BODY
        # =========================

        if (
            not data
            or "identificacion" not in data
            or "telefono" not in data
        ):

            errores += 1

            return jsonify({
                "error": "Identificacion y telefono son obligatorios"
            }), 400

        identificacion = str(data["identificacion"])
        telefono = str(data["telefono"])

        # =========================
        # VALIDAR IDENTIFICACION
        # =========================

        if not identificacion.isdigit():

            errores += 1

            return jsonify({
                "error": "La identificacion solo debe contener numeros"
            }), 400

        # =========================
        # VALIDAR TELEFONO
        # =========================

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

        # =========================
        # VALIDAR DUPLICADOS
        # =========================

        cursor.execute("""
        SELECT * FROM turnos
        WHERE identificacion = %s
        AND estado = 'pendiente'
        """, (identificacion,))

        turno_existente = cursor.fetchone()

        if turno_existente:

            errores += 1

            return jsonify({
                "error": "El usuario ya tiene un turno pendiente"
            }), 400

        # =========================
        # GENERAR NUMERO TURNO
        # =========================

        cursor.execute(
            "SELECT COUNT(*) AS total FROM turnos"
        )

        total_turnos = cursor.fetchone()

        numero_turno = total_turnos["total"] + 1

        codigo_turno = "T" + str(numero_turno)

        fecha = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # =========================
        # INSERTAR TURNO
        # =========================

        cursor.execute("""
        INSERT INTO turnos (
            identificacion,
            telefono,
            turno,
            estado,
            fecha
        )
        VALUES (%s, %s, %s, %s, %s)
        """, (
            identificacion,
            telefono,
            codigo_turno,
            "pendiente",
            fecha
        ))

        conexion.commit()

        turno_id = cursor.lastrowid

        print(
            f"[TURNOS] Turno generado: {codigo_turno}",
            flush=True
        )

        # =========================
        # CIRCUIT BREAKER
        # =========================

        if circuit_breaker == "OPEN":

            print(
                "[CIRCUIT BREAKER] OPEN - Servicio bloqueado",
                flush=True
            )

            time.sleep(5)

            circuit_breaker = "HALF-OPEN"

            print(
                "[CIRCUIT BREAKER] HALF-OPEN",
                flush=True
            )

        # =========================
        # NOTIFICACIONES
        # =========================

        try:

            response = requests.post(
                "http://notificaciones:5000/notificacion",
                json={
                    "telefono": telefono,
                    "mensaje": f"Su turno es {codigo_turno}"
                },
                timeout=3
            )

            if response.status_code != 200:

                fallos_notificaciones += 1

                print(
                    f"[ERROR] Fallo notificaciones: {fallos_notificaciones}",
                    flush=True
                )

            else:

                print(
                    "[NOTIFICACIONES] Enviada correctamente",
                    flush=True
                )

                fallos_notificaciones = 0

                circuit_breaker = "CLOSED"

        except Exception as e:

            fallos_notificaciones += 1

            print(
                f"[ERROR NOTIFICACIONES] {e}",
                flush=True
            )

        # =========================
        # ABRIR CIRCUITO
        # =========================

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
                    "evento": f"Turno generado {codigo_turno}"
                },
                timeout=3
            )

            print(
                "[HISTORIAL] Evento registrado",
                flush=True
            )

        except Exception as e:

            print(
                f"[ERROR HISTORIAL] {e}",
                flush=True
            )

        # =========================
        # MONITOREO
        # =========================

        fin = time.time()

        print(
            f"[MONITOREO] Tiempo respuesta turnos: {fin - inicio:.2f}",
            flush=True
        )

        return jsonify({
            "id": turno_id,
            "identificacion": identificacion,
            "telefono": telefono,
            "turno": codigo_turno,
            "estado": "pendiente",
            "fecha": fecha
        })

    except Exception as e:

        errores += 1

        print(
            f"[ERROR TURNOS] {e}",
            flush=True
        )

        return jsonify({
            "error": str(e)
        }), 500

# =========================
# ACTUALIZAR ESTADO
# =========================

@app.route("/actualizar_turno/<int:id>", methods=["PUT"])
def actualizar_turno(id):

    try:

        data = request.json

        if not data or "estado" not in data:

            return jsonify({
                "error": "Estado requerido"
            }), 400

        estado = data["estado"]

        cursor.execute("""
        UPDATE turnos
        SET estado = %s
        WHERE id = %s
        """, (estado, id))

        conexion.commit()

        if cursor.rowcount == 0:

            return jsonify({
                "error": "Turno no encontrado"
            }), 404

        print(
            f"[TURNOS] Estado actualizado: {estado}",
            flush=True
        )

        return jsonify({
            "mensaje": "Estado actualizado"
        })

    except Exception as e:

        print(
            f"[ERROR TURNOS] {e}",
            flush=True
        )

        return jsonify({
            "error": str(e)
        }), 500

# =========================
# LISTAR TURNOS
# =========================

@app.route("/listar_turnos")
def listar_turnos():

    global peticiones

    peticiones += 1

    print(
        "[TURNOS] Consultando turnos",
        flush=True
    )

    cursor.execute("SELECT * FROM turnos")

    turnos = cursor.fetchall()

    return jsonify({
        "turnos": turnos
    })


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)