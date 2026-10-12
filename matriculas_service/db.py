import os
import time
import psycopg2

def get_db_connection():
    return psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        database=os.getenv('DB_NAME', 'gestion_academica'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres'),
        port=os.getenv('DB_PORT', '5432')
    )

def init_db():
    retries = 5
    while retries > 0:
        try:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('''
                CREATE TABLE IF NOT EXISTS matricula (
                    id SERIAL PRIMARY KEY,
                    estudiante_id INT NOT NULL,
                    curso_id INT NOT NULL,
                    fecha_matricula DATE DEFAULT CURRENT_DATE,
                    estado VARCHAR(50) DEFAULT 'activa'
                );
            ''')
            conn.commit()
            cur.close()
            conn.close()
            print("Tabla matricula inicializada con éxito.")
            break
        except Exception as e:
            print(f"Esperando a la base de datos... ({e})")
            retries -= 1
            time.sleep(2)
            