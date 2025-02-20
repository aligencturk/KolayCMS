# apps paketi başlatma dosyası
from flask import Flask
from apps.extensions import db, login_manager, migrate, babel
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def init_app(app):
    # Veritabanı bağlantısı
    db.init_app(app)
    
    # Login manager ayarları
    login_manager.init_app(app)
    
    # Migrate ayarları
    migrate.init_app(app, db)
    
    # Babel ayarları
    babel.init_app(app)
    
    # CSRF koruması
    csrf.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        from apps.models import User
        return User.query.get(int(user_id))

    # Blueprint'leri içe aktar
    from apps.auth import auth_bp
    from apps.main import main_bp
    from apps.admin import admin_bp
    
    # Blueprint'leri kaydet
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)  # Ana sayfa için önek yok
    app.register_blueprint(admin_bp, url_prefix='/admin') 