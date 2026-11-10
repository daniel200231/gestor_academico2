from flask import Blueprint, jsonify, request
from db import get_connection
import os
import time

DELAY = float(os.getenv("ESTUDIANTES_DELAY", 0))

estudiantes_bp = Blueprint("estudiantes", __name__)

@estudiantes_bp.route("/estudiantes", methods=["GET"])
def listar():
    time.sleep(DELAY) 
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM estudiantes;")
    estudiantes = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(estudiantes), 200

@estudiantes_bp.route("/estudiantes/<int:id>", methods=["GET"])
def obtener(id):
    time.sleep(DELAY)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM estudiantes WHERE id = %s;", (id,))
    estudiante = cur.fetchone()
    cur.close()
    conn.close()

    if estudiante is None:
        return jsonify({"error": "Estudiante no encontrado"}), 404
    
    return jsonify(estudiante), 200

@estudiantes_bp.route("/estudiantes", methods=["POST"])
def crear():
    data = request.get_json()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO estudiantes(cedula, nombre, apellido, correo, programa) 
        VALUES(%s, %s, %s, %s, %s) RETURNING *;
        """,
        (data["cedula"], data["nombre"], data["apellido"], data["correo"], data["programa"])
    )
    nuevo_estudiante = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(nuevo_estudiante), 201

@estudiantes_bp.route("/estudiantes/<int:id>", methods=["PUT"])
def actualizar(id):
    data = request.get_json()
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE estudiantes 
        SET cedula = %s, nombre = %s, apellido = %s, correo = %s, programa = %s 
        WHERE id = %s RETURNING *;
        """,
        (data["cedula"], data["nombre"], data["apellido"], data["correo"], data["programa"], id)
    )
    estudiante_actualizado = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if estudiante_actualizado is None:
        return jsonify({"error": "Estudiante no encontrado"}), 404
    return jsonify(estudiante_actualizado), 200

@estudiantes_bp.route("/estudiantes/<int:id>", methods=["DELETE"])
def eliminar(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM estudiantes WHERE id = %s RETURNING id;", (id,))
    eliminado = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if eliminado is None:
        return jsonify({"error": "No se pudo eliminar el estudiante"}), 404
    return jsonify({"mensaje": "Estudiante eliminado correctamente", "id": id}), 200