from flask import Flask
from flask_cors import CORS
from db import init_db
from routes import estudiantes_bp

app = Flask(__name__)
CORS(app)

# Inicializar las tablas de la BD si no existen
init_db()

# Registrar el Blueprint de estudiantes
app.register_blueprint(estudiantes_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)