import os
import time
import psycopg2
from psycopg2.extras import RealDictCursor

def obtener_conexion():
    intentos = 10
    while intentos > 0:
        try:
            conexion = psycopg2.connect(
                host=os.getenv("DB_HOST"),
                database=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                port=os.getenv("DB_PORT"),
                cursor_factory=RealDictCursor
            )
            return conexion
        except Exception as e:
            print(f"Error conectando a la BD: {e}. Reintentando...")
            time.sleep(3)
            intentos -= 1
    raise Exception("No se pudo conectar a la base de datos tras varios intentos")

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
    