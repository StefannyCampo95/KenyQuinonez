from flask import Flask, jsonify  # type: ignore
import time

app = Flask(__name__)


@app.route("/pagos")
def pagos():

    print("[PAGOS] Procesando pago...", flush=True)

    return jsonify({
        "status": "ok",
        "mensaje": "Pago procesado correctamente"
    })


@app.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "service": "pagos"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)