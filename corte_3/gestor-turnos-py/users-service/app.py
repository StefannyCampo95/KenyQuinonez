from flask import Flask, request, jsonify

app = Flask(__name__)

users = []

@app.route("/users", methods=["GET"])
def get_users():
    return jsonify({
        "mensaje": "Servicio de usuarios funcionando",
        "usuarios_registrados": users
    })

@app.route("/users", methods=["POST"])
def create_user():
    data = request.json

    user = {
        "identificacion": data["identificacion"],
        "telefono": data["telefono"]
    }

    users.append(user)

    return jsonify({"mensaje": "usuario creado", "user": user})

app.run(host="0.0.0.0", port=5000)