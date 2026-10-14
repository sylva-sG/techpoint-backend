import os
from datetime import timedelta
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN")
    DEBUG = os.getenv("FLASK_DEBUG") == "True"
    PORT = int(os.getenv("PORT", 5000))
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    SECRET_KEY = "test-secret"
    JWT_SECRET_KEY = "test-jwt-secret-that-is-long-enough-32b"
    FRONTEND_ORIGIN = "http://localhost:5173"
