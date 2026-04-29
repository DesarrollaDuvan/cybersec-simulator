"""
config.py — Configuración central de la app.
Colócalo en la raíz del proyecto: cybersec-simulator/config.py
"""

import os


class Config:
    # Clave secreta para sesiones (cámbiala en producción)
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-cambiar-en-produccion')

    # Base de datos SQLite local
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'database.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # API Key de Anthropic (se carga desde .env)
    ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')