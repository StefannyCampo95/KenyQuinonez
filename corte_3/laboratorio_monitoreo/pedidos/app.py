from flask import Flask, jsonify # type: ignore
import requests # type: ignore
import time

app = Flask(__name__)

# -----------------------------
# MÉTRICAS
# -----------------------------
errores_pagos = 0
peticiones = 0

# -----------------------------
# PEDIDOS
# -----------------------------
@app.route("/pedidos")
def pedidos():

    global errores_pagos
    global peticiones

    peticiones += 1

    try:

        inicio = time.time()

        print("[PEDIDOS] Consultando inventario...", flush=True)

        inventario = requests.get(
            "http://inventario:5000/inventario",
            timeout=3
        )

        print("[PEDIDOS] Consultando pagos...", flush=True)

        pagos = requests.get(
            "http://pagos:5000/pagos",
            timeout=3
        )

        fin = time.time()

        tiempo = fin - inicio

        print(
            f"[MONITOREO] Tiempo respuesta total: {tiempo:.2f} segundos",
            flush=True
        )

        return jsonify({
            "inventario": inventario.json(),
            "pagos": pagos.json(),
            "tiempo_respuesta": tiempo
        })

    except Exception as e:

        errores_pagos += 1

        print(
            f"[ERROR] Servicio pagos no disponible",
            flush=True
        )

        print(f"[DETALLE] {e}", flush=True)

        return {
            "error": "Error en servicio pagos"
        }, 503


# -----------------------------
# HEALTH CHECK
# -----------------------------
@app.route("/health")
def health():

    return {
        "status": "ok",
        "service": "pedidos"
    }


# -----------------------------
# MONITOREO GENERAL
# -----------------------------
@app.route("/monitor")
def monitor():

    estado = {}

    servicios = {
        "inventario": "http://inventario:5000/health",
        "pagos": "http://pagos:5000/health"
    }

    for nombre, url in servicios.items():

        try:

            response = requests.get(url, timeout=2)

            estado[nombre] = response.json()

        except:

            estado[nombre] = {
                "status": "down"
            }

    return jsonify(estado)


# -----------------------------
# MÉTRICAS
# -----------------------------
@app.route("/metrics")
def metrics():

    return {
        "peticiones_totales": peticiones,
        "errores_pagos": errores_pagos
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)