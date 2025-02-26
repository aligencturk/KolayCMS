from flask import Flask, url_for, render_template, request, current_app
from apps.extensions import db, login_manager, migrate, babel, init_extensions
from flask_wtf.csrf import CSRFProtect
from apps.models import User, SiteSettings, Page, Widget, Menu, Content, ActivityLog, Theme, Product, Category, Order, BlogPost, Slide, Service, AboutSection, VideoSection, TeamMember, Testimonial, ContactInfo
from apps.admin.views import admin_bp
from apps.auth.views import auth_bp
from apps.main.views import main_bp
from apps.admin.views import create_default_content
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import os
import urllib.parse
from sqlalchemy import text
from flask_migrate import Migrate, upgrade
from flask_login import login_required
from apps.admin.views import admin_required

# Global uygulama değişkenleri
app = None
flask_app = None

def create_app():
    global flask_app, app
    
    if flask_app is not None:
        return flask_app
        
    app = Flask(__name__, 
                static_folder='static',
                static_url_path='/static',
                template_folder='templates')
    
    flask_app = app
    
    # CSRF koruması ekle
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    # CSRF ayarları
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600  # 1 saat
    app.config['WTF_CSRF_SSL_STRICT'] = False  # Geliştirme ortamı için SSL kontrolünü devre dışı bırak
    app.config['WTF_CSRF_SECRET_KEY'] = 'your-csrf-secret-key'  # CSRF için özel anahtar
    
    # Debug ayarları
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['FLASK_ADMIN_RAISE_ON_VIEW_EXCEPTION'] = True
    
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
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20
    }
    
    # Uzantıları başlat
    init_extensions(app)
    
    # Blueprint'leri kaydet
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)

    # admin/views/theme.py dosyasındaki theme Blueprint'ini kaydet
    try:
        from flask import Blueprint, render_template, redirect, url_for, flash, request
        theme_bp = Blueprint('theme_bp', __name__)
        
        @theme_bp.route('/templates')
        @login_required
        @admin_required
        def theme_templates():
            return render_template('admin/template_editor/index.html', active_theme=SiteSettings.query.first().active_theme)
        
        app.register_blueprint(theme_bp, url_prefix='/admin/theme')
        app.logger.info('Tema yönetimi Blueprint kaydedildi')
    except Exception as e:
        app.logger.error(f'Tema yönetimi Blueprint kaydedilemedi: {str(e)}')
    
    # Babel için dil ayarları
    app.config['BABEL_DEFAULT_LOCALE'] = 'tr'
    
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
    try:
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
    except PermissionError:
        # Log dosyasına erişim hatası durumunda alternatif log dosyası kullan
        alt_log_file = f'logs/kolaycms_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        file_handler = RotatingFileHandler(
            alt_log_file,
            maxBytes=10240,
            backupCount=5,
            delay=True,
            encoding='utf-8',
            mode='a'
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(file_handler)
        app.logger.warning(f'Ana log dosyasına erişim hatası. Alternatif log dosyası kullanılıyor: {alt_log_file}')
    
    # Console handler ekle
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    console_handler.setLevel(logging.DEBUG)
    app.logger.addHandler(console_handler)
    
    app.logger.setLevel(logging.DEBUG)
    app.logger.info('KolayCMS başlatılıyor')

    # Context processor ekle - settings değişkenini tüm template'lere gönder
    @app.context_processor
    def inject_settings():
        settings = SiteSettings.query.first()
        if not settings:
            settings = SiteSettings(
                site_title='Cobsin',
                site_description='Modern ve Profesyonel Web Sitesi Teması'
            )
            db.session.add(settings)
            db.session.commit()
        return dict(site_settings=settings)
    
    # Context processor ekle - şimdiki zamanı tüm template'lere gönder
    @app.context_processor
    def inject_now():
        return {'now': datetime.now}
    
    # Veritabanı tablolarını oluştur
    with app.app_context():
        try:
            # Veritabanını oluştur
            db.create_all()
            
            # İlk admin kullanıcısını oluştur
            admin_user = User.query.filter_by(role='admin').first()
            if not admin_user:
                admin_user = User(
                    username='admin',
                    email='admin@kolaycms.com',
                    role='admin',
                    is_active=True
                )
                admin_user.set_password('admin123')
                db.session.add(admin_user)
                db.session.commit()
                app.logger.info('Admin kullanıcısı oluşturuldu')
            
            # İlk site ayarlarını oluştur
            # settings = SiteSettings.query.first()
            # if not settings:
            #     settings = SiteSettings(
            #         site_title='KolayCMS',
            #         site_description='Modern ve Kolay Yönetilebilir İçerik Yönetim Sistemi',
            #         theme_version='1.0',
            #         theme_name='default',
            #         is_customized=False
            #     )
            #     db.session.add(settings)
            #     db.session.commit()
            #     app.logger.info('Site ayarları oluşturuldu')
            
            # Varsayılan içerikleri oluştur
            create_default_content()
            
            # Admin kullanıcısını kontrol et
            admin = User.query.filter_by(role='admin').first()
            if not admin:
                app.logger.info('Varsayılan admin kullanıcısı oluşturuluyor')
                admin = User(
                    username='admin',
                    email='admin@kolaycms.com',
                    role='admin',
                    is_active=True
                )
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
            
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Veritabanı oluşturma hatası: {str(e)}')
            raise
    
    return app

def get_app():
    global flask_app
    if not flask_app:
        flask_app = create_app()
    return flask_app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=True)