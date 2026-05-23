from flask import Flask, request, jsonify # type: ignore
import requests # type: ignore
import time
from datetime import datetime

app = Flask(__name__)

# =========================
# VARIABLES
# =========================

turnos = []
contador = 1
peticiones = 0
errores = 0

# =========================
# CIRCUIT BREAKER
# =========================

fallos_notificaciones = 0
circuit_breaker = "CLOSED"

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

    return {
        "peticiones": peticiones,
        "errores": errores,
        "turnos_generados": len(turnos),
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

        for turno in turnos:

            if (
                turno["identificacion"] == identificacion
                and turno["estado"] == "pendiente"
            ):

                errores += 1

                return jsonify({
                    "error": "El usuario ya tiene un turno pendiente"
                }), 400

        # =========================
        # CREAR TURNO
        # =========================

        turno = {
            "id": contador,
            "identificacion": identificacion,
            "telefono": telefono,
            "turno": "T" + str(contador),
            "estado": "pendiente",
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        contador += 1

        turnos.append(turno)

        print(
            f"[TURNOS] Turno generado: {turno['turno']}",
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
                "http://notificaciones:5003/notificacion",
                json={
                    "telefono": telefono,
                    "mensaje": f"Su turno es {turno['turno']}"
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
                "http://historial:5004/guardar_evento",
                json={
                    "evento": f"Turno generado {turno['turno']}"
                }
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

        return jsonify(turno)

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
# CAMBIAR ESTADO
# =========================

@app.route("/actualizar_turno/<int:id>", methods=["PUT"])
def actualizar_turno(id):

    data = request.json

    if not data or "estado" not in data:

        return jsonify({
            "error": "Estado requerido"
        }), 400

    for turno in turnos:

        if turno["id"] == id:

            turno["estado"] = data["estado"]

            print(
                f"[TURNOS] Estado actualizado: {turno['estado']}",
                flush=True
            )

            return jsonify({
                "mensaje": "Estado actualizado",
                "turno": turno
            })

    return jsonify({
        "error": "Turno no encontrado"
    }), 404

# =========================
# LISTAR TURNOS
# =========================

@app.route("/listar_turnos")
def listar_turnos():

    print(
        "[TURNOS] Consultando turnos",
        flush=True
    )

    return jsonify({
        "mensaje": "Servicio turnos funcionando",
        "turnos": turnos
    })

# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5002,
        debug=True
    )