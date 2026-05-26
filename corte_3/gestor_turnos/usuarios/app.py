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
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    identificacion VARCHAR(50) UNIQUE,
    telefono VARCHAR(20),
    fecha_registro VARCHAR(50)
)
""")

conexion.commit()

# =========================
# HOME
# =========================

@app.route("/")
def home():

    return {
        "mensaje": "Servicio usuarios funcionando"
    }

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

    cursor.execute("SELECT COUNT(*) AS total FROM usuarios")

    total = cursor.fetchone()

    return {
        "peticiones": peticiones,
        "errores": errores,
        "usuarios_registrados": total["total"]
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

        cursor.execute(
            "SELECT * FROM usuarios WHERE identificacion = %s",
            (identificacion,)
        )

        usuario_existente = cursor.fetchone()

        if usuario_existente:

            errores += 1

            return jsonify({
                "error": "Usuario ya registrado"
            }), 400

        # =========================
        # FECHA
        # =========================

        fecha_registro = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        # =========================
        # INSERTAR USUARIO
        # =========================

        cursor.execute("""
        INSERT INTO usuarios (
            nombre,
            identificacion,
            telefono,
            fecha_registro
        )
        VALUES (%s, %s, %s, %s)
        """, (
            nombre,
            identificacion,
            telefono,
            fecha_registro
        ))

        conexion.commit()

        print(
            f"[USUARIOS] Usuario registrado: {identificacion}",
            flush=True
        )

        fin = time.time()

        print(
            f"[MONITOREO] Tiempo respuesta usuarios: {fin - inicio:.2f}",
            flush=True
        )

        return jsonify({
            "nombre": nombre,
            "identificacion": identificacion,
            "telefono": telefono,
            "fecha_registro": fecha_registro
        })

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

    cursor.execute(
        "SELECT * FROM usuarios WHERE identificacion = %s",
        (identificacion,)
    )

    usuario = cursor.fetchone()

    if usuario:

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

    cursor.execute("SELECT * FROM usuarios")

    usuarios = cursor.fetchall()

    return jsonify({
        "usuarios": usuarios
    })


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)