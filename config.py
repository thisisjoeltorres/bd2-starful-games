import os

class Config:
    # Configuración de PostgreSQL (Principal del taller)
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "starful_games_db")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "admin123")
    
    # Llave secreta para manejo de sesiones en Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "starful_secret_key_9988")