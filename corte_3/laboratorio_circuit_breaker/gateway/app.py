from flask import Flask, request, jsonify # type: ignore
import requests # type: ignore

app = Flask(__name__)

#Inicializamos los circuitos para cada servicio

circuito = {
    "usuarios": {
        "fallos": 0,
        "abierto": False
    },
    "mascotas": {
        "fallos": 0,
        "abierto": False
    }
}
# Variable global para los circuitos
LIMITE_FALLOS = 3


@app.route("/usuarios")
def usuarios():

    global circuito

    servicio = circuito["usuarios"]

    if servicio["abierto"]:
        return {"error": "Servicio usuarios temporalmente bloqueado"}, 503

    try:

        response = requests.get(
            "http://usuarios:5000/usuarios",
            timeout=2
        )

        servicio["fallos"] = 0

        return jsonify(response.json())

    except:

        servicio["fallos"] += 1

        print(
            f"Fallo usuarios número {servicio['fallos']}",
            flush=True
        )

        if servicio["fallos"] >= LIMITE_FALLOS:

            servicio["abierto"] = True

            print(
                "Circuito usuarios abierto",
                flush=True
            )

        return {"error": "Servicio usuarios no disponible"}, 503




@app.route("/mascotas")
def mascotas():

    global circuito

    servicio = circuito["mascotas"]

    if servicio["abierto"]:
        return {"error": "Servicio mascotas temporalmente bloqueado"}, 503

    try:

        response = requests.get(
            "http://backend:5000/mascotas",
            timeout=2
        )

        servicio["fallos"] = 0

        return jsonify(response.json())

    except:

        servicio["fallos"] += 1

        print(
            f"Fallo mascotas número {servicio['fallos']}",
            flush=True
        )

        if servicio["fallos"] >= LIMITE_FALLOS:

            servicio["abierto"] = True

            print(
                "Circuito mascotas abierto",
                flush=True
            )

        return {"error": "Servicio mascotas no disponible"}, 503



@app.route("/resumen")
def resumen():

    resultado = {}

    #USAMOS LOS CIRCUITOS PARA CONSULTAR AMBOS SERVICIOS

    usuarios_service = circuito["usuarios"]

    if usuarios_service["abierto"]:

        resultado["usuarios"] = "Circuito abierto"

    else:

        try:

            response = requests.get(
                "http://usuarios:5000/usuarios",
                timeout=2
            )

            usuarios_service["fallos"] = 0

            resultado["usuarios"] = response.json()

        except:

            usuarios_service["fallos"] += 1

            print(
                f"Fallo usuarios número {usuarios_service['fallos']}",
                flush=True
            )

            if usuarios_service["fallos"] >= LIMITE_FALLOS:

                usuarios_service["abierto"] = True

                print(
                    "Circuito usuarios abierto",
                    flush=True
                )

            resultado["usuarios"] = "No disponible"

   

    mascotas_service = circuito["mascotas"]

    if mascotas_service["abierto"]:

        resultado["mascotas"] = "Circuito abierto"

    else:

        try:

            response = requests.get(
                "http://backend:5000/mascotas",
                timeout=2
            )

            mascotas_service["fallos"] = 0

            resultado["mascotas"] = response.json()

        except:

            mascotas_service["fallos"] += 1

            print(
                f"Fallo mascotas número {mascotas_service['fallos']}",
                flush=True
            )

            if mascotas_service["fallos"] >= LIMITE_FALLOS:

                mascotas_service["abierto"] = True

                print(
                    "Circuito mascotas abierto",
                    flush=True
                )

            resultado["mascotas"] = "No disponible"

    return jsonify(resultado)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)