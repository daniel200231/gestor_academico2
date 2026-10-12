from flask import Blueprint, request, jsonify
from db import get_db_connection
from psycopg2.extras import RealDictCursor

matriculas_bp = Blueprint('matriculas', __name__)

@matriculas_bp.route('/matriculas', methods=['GET'])
def get_matriculas():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM matricula;')
    matriculas = cur.fetchall()
    cur.close()
    conn.close()
    
    # Convertir campo fecha a texto si existe en la respuesta
    for m in matriculas:
        if m.get('fecha_matricula'):
            m['fecha_matricula'] = str(m['fecha_matricula'])
            
    return jsonify(matriculas), 200

@matriculas_bp.route('/matriculas/<int:id>', methods=['GET'])
def get_matricula(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM matricula WHERE id = %s;', (id,))
    matricula = cur.fetchone()
    cur.close()
    conn.close()
    if matricula is None:
        return jsonify({'error': 'Matricula no encontrada'}), 404
        
    if matricula.get('fecha_matricula'):
        matricula['fecha_matricula'] = str(matricula['fecha_matricula'])
        
    return jsonify(matricula), 200

@matriculas_bp.route('/matriculas', methods=['POST'])
def create_matricula():
    data = request.get_json()
    estudiante_id = data.get('estudiante_id')
    curso_id = data.get('curso_id')
    estado = data.get('estado', 'activa')

    if not estudiante_id or not curso_id:
        return jsonify({'error': 'estudiante_id y curso_id son obligatorios'}), 400

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        'INSERT INTO matricula (estudiante_id, curso_id, estado) VALUES (%s, %s, %s) RETURNING *;',
        (estudiante_id, curso_id, estado)
    )
    new_matricula = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if new_matricula and new_matricula.get('fecha_matricula'):
        new_matricula['fecha_matricula'] = str(new_matricula['fecha_matricula'])

    return jsonify(new_matricula), 201

@matriculas_bp.route('/matriculas/<int:id>', methods=['PUT'])
def update_matricula(id):
    data = request.get_json()
    estudiante_id = data.get('estudiante_id')
    curso_id = data.get('curso_id')
    estado = data.get('estado')

    if not estudiante_id or not curso_id or not estado:
        return jsonify({'error': 'Todos los campos (estudiante_id, curso_id, estado) son obligatorios'}), 400

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        'UPDATE matricula SET estudiante_id = %s, curso_id = %s, estado = %s WHERE id = %s RETURNING *;',
        (estudiante_id, curso_id, estado, id)
    )
    updated_matricula = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if updated_matricula is None:
        return jsonify({'error': 'Matricula no encontrada'}), 404

    if updated_matricula and updated_matricula.get('fecha_matricula'):
        updated_matricula['fecha_matricula'] = str(updated_matricula['fecha_matricula'])

    return jsonify(updated_matricula), 200

@matriculas_bp.route('/matriculas/<int:id>', methods=['DELETE'])
def delete_matricula(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM matricula WHERE id = %s RETURNING id;', (id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if deleted is None:
        return jsonify({'error': 'Matricula no encontrada'}), 404

    return jsonify({'message': 'Matricula eliminada exitosamente'}), 200
