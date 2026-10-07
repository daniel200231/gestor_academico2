import os
import psycopg2

def get_connection():
    return psycopg2.connect(
        host=os.getenv("ESTUDIANTES_DB_HOST"),
        port=os.getenv("ESTUDIANTES_DB_PORT"),
        dbname=os.getenv("ESTUDIANTES_DB_NAME"),
        user=os.getenv("ESTUDIANTES_DB_USER"),
        password=os.getenv("ESTUDIANTES_DB_PASSWORD")
    )  
def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS estudiantes (
            id serial PRIMARY KEY,
            cedula VARCHAR(20) NOT NULL UNIQUE,
            nombre VARCHAR(100) NOT NULL,
            correo VARCHAR(100) NOT NULL UNIQUE,
            programa VARCHAR(100) NOT NULL
          
          )
    """)
    conn.commit()
    cur.close()
    conn.close()    