from flask import Flask, request, jsonify # type: ignore
app= Flask(__name__)

@app.route("/usuarios")
def usuarios():
    return jsonify([
        {"id":1, "nombre": "Stefanny"},
        {"id":2, "nombre":"Michael"}
    ])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)