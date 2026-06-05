import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

def obtener_conexion():
    try:
        connection = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            database=Config.DB_NAME,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD
        )
        return connection
    except Exception as ex:
        print(f"Error crítico al conectar a la base de datos: {ex}")
        return None