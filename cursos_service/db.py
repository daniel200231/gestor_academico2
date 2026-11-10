import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor

def obtener_conexion():
    intentos = 10
    while intentos > 0:
        try:
            conexion = psycopg2.connect(
                host=os.getenv("DB_HOST", "db_cursos"),
                database=os.getenv("DB_NAME", "cursos_db"),
                user=os.getenv("DB_USER", "curso"),
                password=os.getenv("DB_PASSWORD", "123456"),
                port=os.getenv("DB_PORT", "5432"),
                cursor_factory=RealDictCursor
            )
            return conexion
        except Exception as e:
            print(f"Esperando a la base de datos de Cursos... ({e})")
            time.sleep(3)
            intentos -= 1
    raise Exception("No se pudo conectar a la base de datos de Cursos tras varios intentos")

def init_db():
    conexion = obtener_conexion()
    cursor = conexion.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS curso (
            id SERIAL PRIMARY KEY,
            codigo VARCHAR(20) UNIQUE NOT NULL,
            nombre VARCHAR(100) NOT NULL,
            creditos INT NOT NULL,
            semestre INT NOT NULL,
            docente_id INT NOT NULL
        );
    """)
    conexion.commit()
    cursor.close()
    conexion.close()