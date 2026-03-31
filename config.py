import os
from dotenv import load_dotenv

load_dotenv()

def _build_db_url():
    url = os.environ.get('DATABASE_URL', '')
    if not url:
        # Fall back to local SQLite for development
        return 'sqlite:///dev.db'
    # Neon/Heroku use postgres:// — normalize
    if url.startswith('postgres://'):
        url = url.replace('postgres://', 'postgresql://', 1)
    # Use psycopg3 dialect for PostgreSQL connections
    if url.startswith('postgresql://') and '+psycopg' not in url:
        url = url.replace('postgresql://', 'postgresql+psycopg://', 1)
    return url


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = _build_db_url()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
