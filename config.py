import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

class Config:
    # Temel Yapılandırma
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'gizli-anahtar-buraya'
    
    # Veritabanı Yapılandırması
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://localhost\\SQLEXPRESS/FlaskCMS?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes&Trusted_Connection=yes&fast_executemany=true&pool_pre_ping=true&pool_recycle=3600'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30
    }
    
    # Flask-Admin Yapılandırması
    FLASK_ADMIN_SWATCH = 'cerulean'
    
    # Oturum Yapılandırması
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    
    # Upload Yapılandırması
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max-limit
    
    # Cache Yapılandırması
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Mail Yapılandırması
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # Dil ayarları
    BABEL_DEFAULT_LOCALE = 'tr'
    LANGUAGES = ['tr', 'en']
    
    # CDN ayarları
    CDN_DOMAIN = os.getenv('CDN_DOMAIN')
    CDN_HTTPS = True
    
    @staticmethod
    def init_app(app):
        # Upload klasörünü oluştur
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)

class DevelopmentConfig(Config):
    DEBUG = True
    
class ProductionConfig(Config):
    DEBUG = False
    
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig 
}