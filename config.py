import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

class Config:
    """Uygulama konfigürasyonu"""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'default-secret-key-change-in-production'
    
    # Debug ayarları
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    TESTING = os.environ.get('FLASK_TESTING', 'True').lower() == 'true'
    PROPAGATE_EXCEPTIONS = True
    PRESERVE_CONTEXT_ON_EXCEPTION = True
    
    # CSRF Ayarları
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or SECRET_KEY
    WTF_CSRF_TIME_LIMIT = None  # CSRF token süresiz geçerli
    WTF_CSRF_SSL_STRICT = False  # Geliştirme ortamında SSL kontrolünü devre dışı bırak
    
    # Firebase
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')
    FIREBASE_STORAGE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET')
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY')
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
    
    # Uygulama ayarları
    LANGUAGES = ['tr', 'en']
    
    # Admin panel ayarları
    FLASK_ADMIN_SWATCH = 'cerulean'

    # Website ve CMS URL ayarları
    WEBSITE_DOMAIN = os.environ.get('WEBSITE_DOMAIN', 'example.com')  # Ana web sitesi domain
    CMS_SUBDOMAIN = os.environ.get('CMS_SUBDOMAIN', 'cms')  # CMS için subdomain
    
    @property
    def WEBSITE_URL(self):
        """Web sitesi URL'sini döndürür"""
        if self.FLASK_ENV == 'development':
            return 'http://localhost:5000'
        return f'https://{self.WEBSITE_DOMAIN}'
    
    @property
    def CMS_URL(self):
        """CMS URL'sini döndürür"""
        if self.FLASK_ENV == 'development':
            return 'http://localhost:5000/admin'
        return f'https://{self.CMS_SUBDOMAIN}.{self.WEBSITE_DOMAIN}'

class DevelopmentConfig(Config):
    """Geliştirme ortamı konfigürasyonu"""
    DEBUG = True
    DEVELOPMENT = True
    TESTING = True
    PROPAGATE_EXCEPTIONS = True
    PRESERVE_CONTEXT_ON_EXCEPTION = True

class ProductionConfig(Config):
    """Canlı ortam konfigürasyonu"""
    DEBUG = False
    DEVELOPMENT = False
    TESTING = False
    PROPAGATE_EXCEPTIONS = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    
    # Canlı ortamda güvenlik ayarları
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    
    # SSL/TLS zorunluluğu
    SSL_REDIRECT = True

# Ortam seçimi
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 