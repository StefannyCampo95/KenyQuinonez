from flask import Flask, jsonify # type: ignore
import requests # type: ignore
import time

app = Flask(__name__)

# -------------------------
# MÉTRICAS
# -------------------------

peticiones = 0
errores = 0

# -------------------------
# CIRCUIT BREAKER
# -------------------------

fallos_pagos = 0
circuito_abierto = False

# -------------------------
# SISTEMA DISTRIBUIDO
# -------------------------

@app.route("/sistema")
def sistema():

    global peticiones
    global errores
    global fallos_pagos
    global circuito_abierto

    peticiones += 1

    # -------------------------
    # CIRCUITO ABIERTO
    # -------------------------

    if circuito_abierto:

        print(
            "[CIRCUIT BREAKER] Servicio pagos bloqueado",
            flush=True
        )

        return {
            "error": "Servicio pagos temporalmente bloqueado"
        }, 503

    try:

        inicio = time.time()

        # -------------------------
        # PEDIDOS
        # -------------------------

        print(
            "[GATEWAY] Consultando pedidos",
            flush=True
        )

        pedidos = requests.get(
            "http://pedidos:5000/pedidos",
            timeout=3
        )

        # -------------------------
        # INVENTARIO
        # -------------------------

        print(
            "[GATEWAY] Consultando inventario",
            flush=True
        )

        inventario = requests.get(
            "http://inventario:5000/inventario",
            timeout=3
        )

        # -------------------------
        # PAGOS
        # -------------------------

        print(
            "[GATEWAY] Consultando pagos",
            flush=True
        )

        pagos = requests.get(
            "http://pagos:5000/pagos",
            timeout=3
        )

        # Reiniciar fallos si funciona
        fallos_pagos = 0

        fin = time.time()

        print(
            f"[MONITOREO] Tiempo respuesta: {fin - inicio:.2f}",
            flush=True
        )

        return jsonify({
            "pedidos": pedidos.json(),
            "inventario": inventario.json(),
            "pagos": pagos.json()
        })

    except Exception as e:

        errores += 1
        fallos_pagos += 1

        print(
            f"[ERROR] Fallo pagos #{fallos_pagos}",
            flush=True
        )

        print(
            f"[DETALLE] {e}",
            flush=True
        )

        # -------------------------
        # ABRIR CIRCUITO
        # -------------------------

        if fallos_pagos >= 3:

            circuito_abierto = True

            print(
                "[CIRCUIT BREAKER] Circuito abierto",
                flush=True
            )

        return {
            "error": "Servicio pagos no disponible"
        }, 503


# -------------------------
# HEALTH CHECK
# -------------------------

@app.route("/health")
def health():

    print(
        "[HEALTH] Gateway activo",
        flush=True
    )

    return {
        "status": "ok",
        "service": "gateway"
    }


# -------------------------
# MONITOREO
# -------------------------

@app.route("/monitor")
def monitor():

    servicios = {
        "pedidos": "http://pedidos:5000/health",
        "inventario": "http://inventario:5000/health",
        "pagos": "http://pagos:5000/health"
    }

    estados = {}

    for nombre, url in servicios.items():

        try:

            response = requests.get(url, timeout=2)

            estados[nombre] = response.json()

        except:

            estados[nombre] = {
                "status": "down"
            }

    return jsonify(estados)


# -------------------------
# MÉTRICAS
# -------------------------

@app.route("/metrics")
def metrics():

    return {
        "peticiones": peticiones,
        "errores": errores,
        "fallos_pagos": fallos_pagos,
        "circuito_abierto": circuito_abierto
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port= 5000, debug=True)