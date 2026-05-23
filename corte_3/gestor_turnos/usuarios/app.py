from flask import Flask, request, jsonify # type: ignore
import time
from datetime import datetime

app = Flask(__name__)

# =========================
# VARIABLES
# =========================

usuarios = []
peticiones = 0
errores = 0

# =========================
# HEALTH CHECK
# =========================

@app.route("/health")
def health():

    print(
        "[HEALTH] Servicio usuarios activo",
        flush=True
    )

    return {
        "status": "ok",
        "service": "usuarios"
    }

# =========================
# METRICAS
# =========================

@app.route("/metricas")
def metricas():

    return {
        "peticiones": peticiones,
        "errores": errores,
        "usuarios_registrados": len(usuarios)
    }

# =========================
# CREAR USUARIO
# =========================

@app.route("/crear_usuario", methods=["POST"])
def crear_usuario():

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
            or "nombre" not in data
            or "identificacion" not in data
            or "telefono" not in data
        ):

            errores += 1

            return jsonify({
                "error": "Todos los campos son obligatorios"
            }), 400

        nombre = str(data["nombre"]).strip()
        identificacion = str(data["identificacion"])
        telefono = str(data["telefono"])

        # =========================
        # VALIDAR NOMBRE
        # =========================

        if not nombre.replace(" ", "").isalpha():

            errores += 1

            return jsonify({
                "error": "El nombre solo debe contener letras"
            }), 400

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

        for usuario in usuarios:

            if usuario["identificacion"] == identificacion:

                errores += 1

                return jsonify({
                    "error": "Usuario ya registrado"
                }), 400

        # =========================
        # CREAR USUARIO
        # =========================

        nuevo_usuario = {
            "nombre": nombre,
            "identificacion": identificacion,
            "telefono": telefono,
            "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        usuarios.append(nuevo_usuario)

        print(
            f"[USUARIOS] Usuario registrado: {identificacion}",
            flush=True
        )

        fin = time.time()

        print(
            f"[MONITOREO] Tiempo respuesta usuarios: {fin - inicio:.2f}",
            flush=True
        )

        return jsonify(nuevo_usuario)

    except Exception as e:

        errores += 1

        print(
            f"[ERROR USUARIOS] {e}",
            flush=True
        )

        return jsonify({
            "error": str(e)
        }), 500

# =========================
# CONSULTAR USUARIO
# =========================

@app.route("/usuario/<identificacion>")
def obtener_usuario(identificacion):

    global peticiones

    peticiones += 1

    print(
        f"[USUARIOS] Consultando usuario: {identificacion}",
        flush=True
    )

    for usuario in usuarios:

        if usuario["identificacion"] == identificacion:

            return jsonify(usuario)

    return jsonify({
        "error": "Usuario no encontrado"
    }), 404

# =========================
# LISTAR USUARIOS
# =========================

@app.route("/listar_usuarios")
def listar_usuarios():

    global peticiones

    peticiones += 1

    print(
        "[USUARIOS] Consultando usuarios",
        flush=True
    )

    return jsonify({
        "usuarios": usuarios
    })

# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )