# apps paketi başlatma dosyası
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from config import Config
from apps.extensions import db, login_manager, migrate, babel, init_extensions
from apps.models import User
from flask_admin import Admin
import os

admin = Admin(name='KolayCMS', template_mode='bootstrap4')
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Konfigürasyon
    app.config['SECRET_KEY'] = 'dev_csnCkCvqZG0lmScY0iFCCdKCTvXTWjRF' # Prod için değiştirin
    
    # Render'da çalışırken veritabanı yolunu düzenle
    if os.environ.get('RENDER'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/cms.db'
    else:
        db_path = os.path.join(app.instance_path, 'cms.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CSRF_ENABLED'] = True
    app.config['CSRF_SSL_STRICT'] = False # Development için, prod'da True olmalı
    app.config['WTF_CSRF_SECRET_KEY'] = 'csrf-secret-key'  # CSRF için özel anahtar
    app.config['WTF_CSRF_TIME_LIMIT'] = None  # CSRF token zaman sınırı kaldırıldı
    
    # Uzantıları başlat
    init_extensions(app)
    csrf.init_app(app)
    
    # Blueprint'leri kaydet
    from apps.admin import admin_bp
    from apps.main import main_bp
    from apps.auth import auth_bp
    
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Admin panelini başlat
    admin.init_app(app)
    
    # Admin görünümlerini başlat
    from apps.admin.views import init_admin
    init_admin(admin)
    
    return app

def init_app(app):
    # Veritabanı bağlantısı
    db.init_app(app)
    
    # Login manager ayarları
    login_manager.init_app(app)
    
    # CSRF koruması
    csrf.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        from apps.models import User
        return User.query.get(int(user_id))

    # NOT: Blueprint'ler zaten create_app() içinde kaydedildiği için burada tekrar kaydedilmemeli 