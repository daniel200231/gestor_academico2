from flask import Flask
from db import init_db
from routes import matriculas_bp

app = Flask(__name__)
app.register_blueprint(matriculas_bp)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5003, debug=True)
    