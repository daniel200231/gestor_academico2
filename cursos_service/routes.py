from flask import Blueprint, request, jsonify
from db import obtener_conexion

cursos_bp = Blueprint('cursos', __name__)

@cursos_bp.route('/cursos', methods=['GET'])
def listar_cursos():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM curso;")
    cursos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jsonify(cursos), 200

@cursos_bp.route('/cursos/<int:id>', methods=['GET'])
def obtener_curso(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM curso WHERE id = %s;", (id,))
    curso = cursor.fetchone()
    cursor.close()
    conexion.close()
    if curso:
        return jsonify(curso), 200
    return jsonify({'mensaje': 'Curso no encontrado'}), 404

@cursos_bp.route('/cursos', methods=['POST'])
def crear_curso():
    data = request.get_json()
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        INSERT INTO curso (codigo, nombre, creditos, semestre, docente_id)
        VALUES (%s, %s, %s, %s, %s) RETURNING *;
    """, (data['codigo'], data['nombre'], data['creditos'], data['semestre'], data['docente_id']))
    nuevo_curso = cursor.fetchone()
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify(nuevo_curso), 201

@cursos_bp.route('/cursos/<int:id>', methods=['PUT'])
def actualizar_curso(id):
    data = request.get_json()
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        UPDATE curso 
        SET codigo = %s, nombre = %s, creditos = %s, semestre = %s, docente_id = %s
        WHERE id = %s RETURNING *;
    """, (data['codigo'], data['nombre'], data['creditos'], data['semestre'], data['docente_id'], id))
    curso_actualizado = cursor.fetchone()
    conexion.commit()
    cursor.close()
    conexion.close()
    if curso_actualizado:
        return jsonify(curso_actualizado), 200
    return jsonify({'mensaje': 'Curso no encontrado'}), 404

@cursos_bp.route('/cursos/<int:id>', methods=['DELETE'])
def eliminar_curso(id):
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM curso WHERE id = %s RETURNING id;", (id,))
    eliminado = cursor.fetchone()
    conexion.commit()
    cursor.close()
    conexion.close()
    if eliminado:
        return jsonify({'mensaje': 'Curso eliminado correctamente'}), 200
    return jsonify({'mensaje': 'Curso no encontrado'}), 404
