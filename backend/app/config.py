import os
from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://charity:charity@db:5432/charity_platform")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-in-prod")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "/tmp/charity_uploads")
    NATIONAL_ID_KEY = os.getenv("NATIONAL_ID_KEY", "0123456789abcdef0123456789abcdef")
