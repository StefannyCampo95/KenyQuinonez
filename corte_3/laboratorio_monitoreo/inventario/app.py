from flask import Flask, jsonify # type: ignore
import time

app = Flask(__name__)

@app.route("/inventario")
def inventario():

    print("[INVENTARIO] Consultando productos...", flush=True)

    time.sleep(1)

    return jsonify([
        {
            "producto": "Blusas",
            "stock": 10
        },
        {
            "producto": "Pantalones",
            "stock": 20
        }
    ])


@app.route("/health")
def health():

    return {
        "status": "ok",
        "service": "inventario"
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)