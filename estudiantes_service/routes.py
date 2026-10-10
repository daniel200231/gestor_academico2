from flask import Blueprint, jsonify
from db import get_connection

estudiantes_bp = Blueprint("estudiantes", __name__)

@estudiantes_bp.route("/estudiantes", methods=["GET"])
def listar():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, cedula, nombre, apellido, correo, programa FROM estudiantes")
    filas = cur.fetchall()
    cur.close()
    conn.close()
    estudiantes = [
        {"id": f[0], "cedula": f[1], "nombre": f[2], "apellido": f[3], "correo": f[4], "programa": f[5]}
        for f in filas
    ]
    return jsonify(estudiantes), 200