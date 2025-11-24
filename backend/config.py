import os
from datetime import timedelta

class Config:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # MongoDB
    MONGO_URI = os.environ.get('MONGODB_URI') or os.environ.get('MONGO_URI') or 'mongodb://localhost:27017/rfprag'
    MONGO_DATABASE = os.environ.get('MONGO_DATABASE') or 'rfp_db'
    
    # File upload
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size
    ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'pdf', 'docx'}
    
    # Vector database
    VECTOR_DB_URL = os.environ.get('VECTOR_DB_URL') or 'http://localhost:6333'
    VECTOR_COLLECTION = 'rfp_documents'
    EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    
    # Celery
    CELERY_BROKER_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL') or 'redis://localhost:6379/0'
    
    # JWT
    JWT_SECRET_KEY = SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:8080,http://localhost:3000').split(',')