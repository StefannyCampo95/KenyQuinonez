from flask import Flask, jsonify # type: ignore
import time

app = Flask(__name__)

peticiones = 0

# -------------------------
# INVENTARIO
# -------------------------

@app.route("/inventario")
def inventario():

    global peticiones

    peticiones += 1

    inicio = time.time()

    print(
        "[INVENTARIO] Consultando stock",
        flush=True
    )

    inventario = [
        {
            "producto": "Laptop",
            "stock": 10
        },
        {
            "producto": "Mouse",
            "stock": 20
        }
    ]

    fin = time.time()

    print(
        f"[MONITOREO] Tiempo respuesta inventario: {fin - inicio:.2f}",
        flush=True
    )

    return jsonify(inventario)


# -------------------------
# HEALTH CHECK
# -------------------------

@app.route("/health")
def health():

    print(
        "[HEALTH] Servicio inventario activo",
        flush=True
    )

    return {
        "status": "ok",
        "service": "inventario"
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
    app.run(host="0.0.0.0", port=5000)