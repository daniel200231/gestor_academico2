
from flask import Blueprint, request, jsonify
from db import get_db_connection
from psycopg2.extras import RealDictCursor
import os
import requests
import pybreaker

# 1. Variables de entorno para comunicación y resiliencia
ESTUDIANTES_URL = os.getenv("ESTUDIANTES_URL", "http://estudiantes:5002")
CURSOS_URL = os.getenv("CURSOS_URL", "http://cursos_service:5000")
HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", 3))
CB_FAIL_MAX = int(os.getenv("CB_FAIL_MAX", 3))
CB_RESET_TIMEOUT = int(os.getenv("CB_RESET_TIMEOUT", 30))

# 2. Instanciación de los Circuit Breakers
breaker_estudiantes = pybreaker.CircuitBreaker(
    fail_max=CB_FAIL_MAX,
    reset_timeout=CB_RESET_TIMEOUT,
    throw_new_error_on_trip=False,
    name="EstudiantesBreaker"
)

breaker_cursos = pybreaker.CircuitBreaker(
    fail_max=CB_FAIL_MAX,
    reset_timeout=CB_RESET_TIMEOUT,
    throw_new_error_on_trip=False,
    name="CursosBreaker"
)

matriculas_bp = Blueprint('matriculas', __name__)

# 3. Endpoint de diagnóstico de los Circuit Breakers
@matriculas_bp.route('/circuit-status', methods=['GET'])
def circuit_status():
    return jsonify({
        "estudiantes_circuit": breaker_estudiantes.current_state,
        "cursos_circuit": breaker_cursos.current_state
    }), 200


# 4. Consultar todas las matrículas
@matriculas_bp.route('/matriculas', methods=['GET'])
def get_matriculas():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute('SELECT * FROM matricula;')
    matriculas = cur.fetchall()
    cur.close()
    conn.close()

    for m in matriculas:
        if m.get('fecha_matricula'):
            m['fecha_matricula'] = str(m['fecha_matricula'])

    return jsonify(matriculas), 200


# 5. Consultar una matrícula por ID
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


# 6. Crear matrícula con validación de microservicios
@matriculas_bp.route('/matriculas', methods=['POST'])
def create_matricula():
    data = request.get_json() or {}
    estudiante_id = data.get('estudiante_id')
    curso_id = data.get('curso_id')
    estado = data.get('estado', 'activa')

    if not estudiante_id or not curso_id:
        return jsonify({
            'error': 'estudiante_id y curso_id son obligatorios'
        }), 400

    # VALIDACIÓN 1: SERVICIO DE ESTUDIANTES
    try:
        @breaker_estudiantes
        def consultar_estudiante():
            return requests.get(
                f"{ESTUDIANTES_URL}/estudiantes/{estudiante_id}",
                timeout=HTTP_TIMEOUT
            )

        r_est = consultar_estudiante()

        if r_est.status_code == 404:
            return jsonify({"error": "El estudiante no existe"}), 404

        if r_est.status_code >= 500:
            r_est.raise_for_status()

    except pybreaker.CircuitBreakerError:
        return jsonify({
            "error": "Circuito ABIERTO: Servicio de Estudiantes fallando repetidamente"
        }), 503

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Gateway Timeout: Servicio de Estudiantes tardó demasiado en responder"
        }), 504

    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Service Unavailable: No se pudo conectar con el servicio de Estudiantes"
        }), 503

    except requests.exceptions.HTTPError:
        return jsonify({
            "error": "Error en la respuesta del servicio de Estudiantes"
        }), 502

    # VALIDACIÓN 2: SERVICIO DE CURSOS
    try:
        @breaker_cursos
        def consultar_curso():
            return requests.get(
                f"{CURSOS_URL}/cursos/{curso_id}",
                timeout=HTTP_TIMEOUT
            )

        r_cur = consultar_curso()

        if r_cur.status_code == 404:
            return jsonify({"error": "El curso no existe"}), 404

        if r_cur.status_code >= 500:
            r_cur.raise_for_status()

    except pybreaker.CircuitBreakerError:
        return jsonify({
            "error": "Circuito ABIERTO: Servicio de Cursos fallando repetidamente"
        }), 503

    except requests.exceptions.Timeout:
        return jsonify({
            "error": "Gateway Timeout: Servicio de Cursos tardó demasiado en responder"
        }), 504

    except requests.exceptions.ConnectionError:
        return jsonify({
            "error": "Service Unavailable: No se pudo conectar con el servicio de Cursos"
        }), 503

    except requests.exceptions.HTTPError:
        return jsonify({
            "error": "Error en la respuesta del servicio de Cursos"
        }), 502

    # 7. PERSISTENCIA EN LA BASE DE DATOS DE MATRÍCULAS
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        '''INSERT INTO matricula
        (estudiante_id, curso_id, estado)
        VALUES (%s, %s, %s) RETURNING *;''',
        (estudiante_id, curso_id, estado)
    )

    new_matricula = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if new_matricula and new_matricula.get('fecha_matricula'):
        new_matricula['fecha_matricula'] = str(
            new_matricula['fecha_matricula']
        )

    return jsonify(new_matricula), 201


# 8. Actualizar matrícula
@matriculas_bp.route('/matriculas/<int:id>', methods=['PUT'])
def update_matricula(id):
    data = request.get_json() or {}
    estudiante_id = data.get('estudiante_id')
    curso_id = data.get('curso_id')
    estado = data.get('estado')

    if not estudiante_id or not curso_id or not estado:
        return jsonify({
            'error': 'Todos los campos son obligatorios'
        }), 400

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute(
        '''UPDATE matricula
        SET estudiante_id = %s, curso_id = %s, estado = %s
        WHERE id = %s RETURNING *;''',
        (estudiante_id, curso_id, estado, id)
    )

    updated_matricula = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if updated_matricula is None:
        return jsonify({'error': 'Matricula no encontrada'}), 404

    if updated_matricula.get('fecha_matricula'):
        updated_matricula['fecha_matricula'] = str(
            updated_matricula['fecha_matricula']
        )

    return jsonify(updated_matricula), 200


# 9. Eliminar matrícula
@matriculas_bp.route('/matriculas/<int:id>', methods=['DELETE'])
def delete_matricula(id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        'DELETE FROM matricula WHERE id = %s RETURNING id;',
        (id,)
    )

    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    if deleted is None:
        return jsonify({'error': 'Matricula no encontrada'}), 404

    return jsonify({
        'message': 'Matricula eliminada exitosamente'
    }), 200
