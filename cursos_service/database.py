import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time

def connectar():
    for intento in range(10):
        try:
            conexion = psycopg2.connect(
                host=os.getenv('DB_HOST', 'postgres_db'),
                port=int(os.getenv('DB_PORT', 5432)),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres'),
                dbname=os.getenv('DB_NAME', 'gestor_academico')
            )
            # Creacion automatica de la tabla cursos si no existe
            cursor = conexion.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cursos (
                    id SERIAL PRIMARY KEY,
                    codigo VARCHAR(20) UNIQUE NOT NULL,
                    nombre VARCHAR(100) NOT NULL,
                    creditos INT NOT NULL,
                    semestre INT NOT NULL,
                    docente_id INT
                );
            """)
            conexion.commit()
            cursor.close()
            return conexion
        except Exception as err:
            print(f"Error al conectar a la base de datos: {err}")
            time.sleep(5)
    raise Exception("No se pudo conectar a la base de datos después de varios intentos.")
