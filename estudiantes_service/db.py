import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor

def get_connection():
    intentos = 10
    while intentos > 0:
        try:
            conn = psycopg2.connect(
                host=os.getenv("ESTUDIANTES_DB_HOST", "db_estudiantes"),
                port=os.getenv("ESTUDIANTES_DB_PORT", "5432"),
                dbname=os.getenv("ESTUDIANTES_DB_NAME", "estudiantes_service"),
                user=os.getenv("ESTUDIANTES_DB_USER", "estudiante"),
                password=os.getenv("ESTUDIANTES_DB_PASSWORD", "123456"),
                cursor_factory=RealDictCursor
            )
            return conn
        except Exception as e:
            print(f"Esperando a la base de datos de Estudiantes... ({e})")
            time.sleep(3)
            intentos -= 1
    raise Exception("No se pudo conectar a la base de datos de Estudiantes tras varios intentos")

def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS estudiantes (
            id SERIAL PRIMARY KEY,
            cedula VARCHAR(20) NOT NULL UNIQUE,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            correo VARCHAR(100) NOT NULL UNIQUE,
            programa VARCHAR(100) NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()