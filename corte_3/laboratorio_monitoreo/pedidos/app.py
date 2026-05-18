from flask import Flask, jsonify # type: ignore
import time

app = Flask(__name__)

peticiones = 0

# -------------------------
# PEDIDOS
# -------------------------

@app.route("/pedidos")
def pedidos():

    global peticiones

    peticiones += 1

    inicio = time.time()

    print(
        "[PEDIDOS] Consultando pedidos",
        flush=True
    )

    pedidos = [
        {
            "id": 1,
            "producto": "Laptop"
        },
        {
            "id": 2,
            "producto": "Mouse"
        }
    ]

    fin = time.time()

    print(
        f"[MONITOREO] Tiempo respuesta pedidos: {fin - inicio:.2f}",
        flush=True
    )

    return jsonify(pedidos)


# -------------------------
# HEALTH CHECK
# -------------------------

@app.route("/health")
def health():

    print(
        "[HEALTH] Servicio pedidos activo",
        flush=True
    )

    return {
        "status": "ok",
        "service": "pedidos"
    }


# -------------------------
# MÉTRICAS
# -------------------------

@app.route("/metrics")
def metrics():

    return {
        "peticiones": peticiones
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port= 5000, debug=True)