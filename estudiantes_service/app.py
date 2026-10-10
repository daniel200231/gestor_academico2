from flask import Flask, jsonify
from db import init_db
from routes import estudiantes_bp

app = Flask(__name__)
app.register_blueprint(estudiantes_bp)

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5002)