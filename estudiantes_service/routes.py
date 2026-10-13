from flask import Blueprint, jsonify, request
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
@estudiantes_bp.route("/estudiantes/<int:id>", methods=["GET"])
def obtener(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, cedula, nombre, apellido, correo, programa FROM estudiantes WHERE id = %s",
        (id,)
    )
    f = cur.fetchone()
    cur.close()
    conn.close()

    if f is None:
        return jsonify({"error": "Estudiante no encontrado"}), 404
    
    return jsonify({
        "id": f[0],
        "cedula": f[1],
        "nombre": f[2],
        "apellido": f[3],
        "correo": f[4],
        "programa": f[5]
    }),200

@estudiantes_bp.route("/estudiantes", methods=["POST"])
def crear():
    data = request.get_json()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO estudiantes(cedula, nombre, apellido, correo, programa) VALUES(%s, %s, %s, %s, %s) RETURNING id",
        (data["cedula"], data["nombre"], data["apellido"], data["correo"], data["programa"])
    )
    nuevo_id= cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"mensaje": "estudiante creado", "id": nuevo_id}),201

@estudiantes_bp.route("/estudiantes/<int:id>", methods=["PUT"])
def actualizar(id):
    data = request.get_json()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE estudiantes SET cedula = %s, nombre = %s, apellido = %s, correo = %s, programa = %s WHERE id = %s",
        (data["cedula"], data["nombre"], data["apellido"], data["correo"], data["programa"], id)
    )
    filas = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if filas == 0:
        return jsonify({"error": "Estudiante no encontrado"}), 404
    return jsonify({"mensaje": "estudiante actualizado", "id": id}), 200

@estudiantes_bp.route("/estudiantes/<int:id>", methods=["DELETE"])
def elimiar(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
          "DELETE FROM estudiantes WHERE id = %s",
        (id,)
    )
    filas = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if filas == 0:
        return jsonify({"error": "no se puede eliminar el estudiante"}), 404
    return jsonify({"mensaje": "estudiante eliminado", "id": id}), 200