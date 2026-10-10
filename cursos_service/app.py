from flask import Flask
from db import init_db
from routes import cursos_bp

app = Flask(__name__)

# Inicializar las tablas si no existen
init_db()

# Registrar rutas
app.register_blueprint(cursos_bp)

if __name__ == '__main__':
    app.run(host='' \
    '0.0.0.0', port=5000, debug=True)
    