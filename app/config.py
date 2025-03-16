import os
from datetime import timedelta

class Config:
    """Temel konfigürasyon sınıfı"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=60)
    
    # Ana dizin
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Tema dizinleri
    THEMES_FOLDER = os.path.join(BASE_DIR, 'themes')
    UPLOAD_FOLDER = os.path.join(THEMES_FOLDER, 'uploads')
    THEMES_TEMPLATE_FOLDER = os.path.join(THEMES_FOLDER, 'templates')
    THEMES_STATIC_FOLDER = os.path.join(THEMES_FOLDER, 'static')
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'zip', 'rar', 'html', 'css', 'js'}
    
    # Firebase yapılandırması
    FIREBASE_CONFIG = {
        "type": "service_account",
        "project_id": "kolaycms",
        "private_key_id": os.environ.get('FIREBASE_PRIVATE_KEY_ID'),
        "private_key": os.environ.get('FIREBASE_PRIVATE_KEY', '').replace('\\n', '\n'),
        "client_email": os.environ.get('FIREBASE_CLIENT_EMAIL'),
        "client_id": os.environ.get('FIREBASE_CLIENT_ID'),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ.get('FIREBASE_CLIENT_CERT_URL')
    }

class DevelopmentConfig(Config):
    """Geliştirme ortamı konfigürasyonu"""
    DEBUG = True
    TESTING = True

class ProductionConfig(Config):
    """Üretim ortamı konfigürasyonu"""
    DEBUG = False
    TESTING = False

# Konfigürasyon sözlüğü
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 