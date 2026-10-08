from flask import Flask
from routes import cursos_bp

app = Flask(__name__)

app.register_blueprint(cursos_bp)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
    