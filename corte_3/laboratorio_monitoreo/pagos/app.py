from flask import Flask, jsonify # type: ignore
import random
import time

app = Flask(__name__)

@app.route("/pagos")
def pagos():

    print("[PAGOS] Procesando pago...", flush=True)

    time.sleep(2)

    fallo = random.randint(1, 5)

    # Simular fallos aleatorios
    if fallo >= 3:

        print(
            "[ERROR] Fallo procesando pago",
            flush=True
        )

        return jsonify({
            "status": "error",
            "mensaje": "No fue posible procesar el pago"
        }), 500

    return jsonify({
        "status": "ok",
        "mensaje": "Pago procesado correctamente"
    })


@app.route("/health")
def health():

    return {
        "status": "ok",
        "service": "pagos"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)