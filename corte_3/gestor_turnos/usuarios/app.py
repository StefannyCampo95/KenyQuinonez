from flask import Flask, request, jsonify # type: ignore
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
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100),
    identificacion VARCHAR(20) UNIQUE,
    telefono VARCHAR(20),
    fecha_registro DATETIME
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
        "service": "usuarios"
    }

# =========================
# METRICAS
# =========================

@app.route("/metricas")
def metricas():

    return {
        "peticiones": peticiones,
        "errores": errores
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

        if (
            not data
            or "nombre" not in data
            or "identificacion" not in data
            or "telefono" not in data
        ):

            return jsonify({
                "error": "Todos los campos son obligatorios"
            }), 400

        nombre = str(data["nombre"]).strip()
        identificacion = str(data["identificacion"])
        telefono = str(data["telefono"])

        if not nombre.replace(" ", "").isalpha():

            return jsonify({
                "error": "El nombre solo debe contener letras"
            }), 400

        if not identificacion.isdigit():

            return jsonify({
                "error": "La identificacion solo debe contener numeros"
            }), 400

        if not telefono.isdigit():

            return jsonify({
                "error": "El telefono solo debe contener numeros"
            }), 400

        if len(telefono) != 10:

            return jsonify({
                "error": "El telefono debe tener 10 digitos"
            }), 400

        cursor.execute(
            "SELECT * FROM usuarios WHERE identificacion = %s",
            (identificacion,)
        )

        usuario_existente = cursor.fetchone()

        if usuario_existente:

            return jsonify({
                "error": "Usuario ya registrado"
            }), 400

        fecha = datetime.now()

        cursor.execute("""
            INSERT INTO usuarios
            (nombre, identificacion, telefono, fecha_registro)
            VALUES (%s, %s, %s, %s)
        """, (
            nombre,
            identificacion,
            telefono,
            fecha
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
            "telefono": telefono
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
# LISTAR USUARIOS
# =========================

@app.route("/listar_usuarios")
def listar_usuarios():

    cursor.execute("SELECT * FROM usuarios")

    resultados = cursor.fetchall()

    usuarios = []

    for usuario in resultados:

        usuarios.append({
            "id": usuario[0],
            "nombre": usuario[1],
            "identificacion": usuario[2],
            "telefono": usuario[3]
        })

    return jsonify({
        "usuarios": usuarios
    })


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)