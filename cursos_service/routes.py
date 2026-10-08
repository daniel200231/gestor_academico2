from flask import Blueprint, jsonify, request
from database import connectar
from psycopg2.extras import RealDictCursor

cursos_bp = Blueprint('cursos', __name__)

@cursos_bp.route('/cursos', methods=['GET'])
def obtener_cursos():
    conexion = connectar()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM cursos;")
    cursos = cursor.fetchall()
    cursor.close()
    conexion.close()
    return jsonify(cursos)

@cursos_bp.route('/cursos/<int:id>', methods=['GET'])
def buscar(id):
    conexion = connectar()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    sql = "SELECT * FROM cursos WHERE id = %s;"
    cursor.execute(sql, (id,))
    curso = cursor.fetchone()
    cursor.close()
    conexion.close()
    if curso is None:
        return jsonify({"error": "Curso no encontrado"}), 404
    return jsonify(curso)

@cursos_bp.route('/cursos', methods=['POST'])
def agregar_curso():
    nuevo_curso = request.json
    conexion = connectar()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    sql = """
        INSERT INTO cursos (codigo, nombre, creditos, semestre, docente_id)
        VALUES (%s, %s, %s, %s, %s) RETURNING id;
    """
    cursor.execute(sql, (
        nuevo_curso['codigo'],
        nuevo_curso['nombre'],
        nuevo_curso['creditos'],
        nuevo_curso['semestre'],
        nuevo_curso.get('docente_id')
    ))
    nuevo_id = cursor.fetchone()['id']
    conexion.commit()
    cursor.close()
    conexion.close()
    return jsonify({"Mensaje": "Curso agregado correctamente", "id": nuevo_id}), 201

@cursos_bp.route('/cursos/<int:id>', methods=['PUT'])
def actualizar_curso(id):
    datos = request.json
    conexion = connectar()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    sql = "UPDATE cursos SET nombre = %s, creditos = %s WHERE id = %s;"
    cursor.execute(sql, (datos['nombre'], datos['creditos'], id))
    conexion.commit()
    filas_afectadas = cursor.rowcount
    cursor.close()
    conexion.close()
    if filas_afectadas == 0:
        return jsonify({"error": "Curso no encontrado"}), 404
    return jsonify({"Mensaje": "Curso actualizado correctamente"})

@cursos_bp.route('/cursos/<int:id>', methods=['DELETE'])
def eliminar_curso(id):
    conexion = connectar()
    cursor = conexion.cursor(cursor_factory=RealDictCursor)
    sql = "DELETE FROM cursos WHERE id = %s;"
    cursor.execute(sql, (id,))
    conexion.commit()
    filas_afectadas = cursor.rowcount
    cursor.close()
    conexion.close()
    if filas_afectadas == 0:
        return jsonify({"error": "Curso no encontrado"}), 404
    return jsonify({"Mensaje": "Curso eliminado correctamente"})
