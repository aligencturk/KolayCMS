from flask import Flask, url_for, render_template
from apps.extensions import db, login_manager, migrate, babel
from apps.models import User, SiteSettings, Page, Widget, Menu, Content, ActivityLog, Theme, Product, Category, Order
import logging
from logging.handlers import RotatingFileHandler
import os
import urllib.parse
from sqlalchemy import text
from flask_migrate import Migrate, upgrade

def create_app():
    app = Flask(__name__, 
                static_folder='static',
                static_url_path='/static',
                template_folder='templates')
    
    # Debug ayarları
    app.config['DEBUG'] = False
    app.config['SQLALCHEMY_ECHO'] = False
    app.config['FLASK_ADMIN_RAISE_ON_VIEW_EXCEPTION'] = False
    
    # HTTPS olmadan çalışabilmesi için
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    
    app.config['SECRET_KEY'] = 'your-secret-key'
    
    # SQLite bağlantı ayarları
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, 'kolaycms.db')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300
    }
    
    # Uzantıları başlat
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    babel.init_app(app)
    
    # Upload klasörü ayarları
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'logos'))
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'images'))

    # Loglama ayarları
    if not os.path.exists('logs'):
        os.makedirs('logs', exist_ok=True)
    
    # Eski log handler'ları temizle
    for handler in app.logger.handlers[:]:
        app.logger.removeHandler(handler)
    
    # Yeni log handler'ı oluştur
    file_handler = RotatingFileHandler(
        'logs/kolaycms.log',
        maxBytes=10240,
        backupCount=10,
        delay=True,
        encoding='utf-8',
        mode='a'  # Append mode
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(file_handler)
    
    # Console handler ekle
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    console_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(console_handler)
    
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('KolayCMS başlatılıyor')

    # Blueprint'leri kaydet
    from apps.auth.views import auth_bp
    from apps.main.views import main_bp
    from apps.admin import admin_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
    # Babel için dil ayarları
    app.config['BABEL_DEFAULT_LOCALE'] = 'tr'
    
    # Veritabanı tablolarını oluştur
    with app.app_context():
        try:
            # Önce migrationları uygula
            upgrade()
            
            # İlk admin kullanıcısını oluştur
            admin_user = User.query.filter_by(role='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@kolaycms.com',
                    role='admin'
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                app.logger.info('Admin kullanıcısı oluşturuldu')
            
            # İlk site ayarlarını oluştur
            settings = SiteSettings.query.first()
            if not settings:
                settings = SiteSettings(
                    site_title='KolayCMS',
                    site_description='Modern ve Kolay Yönetilebilir İçerik Yönetim Sistemi',
                    theme_version='1.0',
                    theme_name='default',
                    is_customized=False
                )
                db.session.add(settings)
                db.session.commit()
                app.logger.info('Site ayarları oluşturuldu')
                    
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Veritabanı oluşturma hatası: {str(e)}')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5001)