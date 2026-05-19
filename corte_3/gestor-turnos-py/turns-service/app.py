from flask import Flask, request, jsonify

app = Flask(__name__)

turnos = []
contador = 1

@app.route("/turn", methods=["POST"])
def crear_turno():

    global contador

    data = request.json

    turno = {
        "identificacion": data["identificacion"],
        "turno": "T" + str(contador)
    }

    contador += 1

    turnos.append(turno)

    return jsonify(turno)

@app.route("/turns", methods=["GET"])
def listar_turnos():
    return jsonify({
        "mensaje": "Servicio de turnos funcionando",
        "turnos": turnos
    })

app.run(host="0.0.0.0", port=5000)