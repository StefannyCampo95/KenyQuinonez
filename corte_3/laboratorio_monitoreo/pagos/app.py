from flask import Flask, jsonify # type: ignore
import time

app = Flask(__name__)

peticiones = 0

# -------------------------
# PAGOS
# -------------------------

@app.route("/pagos")
def pagos():

    global peticiones

    peticiones += 1

    inicio = time.time()

    print(
        "[PAGOS] Procesando pagos",
        flush=True
    )

    pago = {
        "status": "ok",
        "mensaje": "Pago realizado correctamente"
    }

    fin = time.time()

    print(
        f"[MONITOREO] Tiempo respuesta pagos: {fin - inicio:.2f}",
        flush=True
    )

    return jsonify(pago)


# -------------------------
# HEALTH CHECK
# -------------------------

@app.route("/health")
def health():

    print(
        "[HEALTH] Servicio pagos activo",
        flush=True
    )

    return {
        "status": "ok",
        "service": "pagos"
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