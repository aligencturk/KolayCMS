import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    """Uygulama konfigürasyonu"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-secret-key-change-in-production'
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH') or 'kolaycms-8c482-firebase-adminsdk-fbsvc-4d87537ea9.json'
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID') or 'kolaycms-8c482'
    FIREBASE_STORAGE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET')
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY') or 'AIzaSyCPxvPBq2JF7t3YDLZ45Ykd9Ruj5-JHeHg'
    FIREBASE_CREDENTIALS_JSON = os.environ.get('FIREBASE_CREDENTIALS_JSON')
    
    # Dosya yükleme
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app/static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}
    
    # Dil ayarları
    BABEL_DEFAULT_LOCALE = 'tr'
    BABEL_DEFAULT_TIMEZONE = 'Europe/Istanbul'

    # Flask ayarları
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = FLASK_ENV == 'development'
    
    # Uygulama ayarları
    LANGUAGES = ['tr', 'en']
    
    # Admin panel ayarları
    FLASK_ADMIN_SWATCH = 'cerulean' 