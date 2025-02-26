from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_babel import Babel
from flask import g, current_app

# Uzantıları oluştur
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
babel = Babel()

@login_manager.user_loader
def load_user(user_id):
    from apps.models import User
    return User.query.get(int(user_id))

def init_extensions(app):
    """Tüm Flask uzantılarını başlat"""
    
    # SQLAlchemy'yi başlat
    db.init_app(app)
    
    # Login manager ayarları
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Lütfen giriş yapın.'
    login_manager.login_message_category = 'info'
    
    # Migrate ve Babel'i başlat
    migrate.init_app(app, db)
    babel.init_app(app)
    
    return app

def get_db():
    """Veritabanı bağlantısını döndür"""
    if not hasattr(g, 'db'):
        g.db = db
        # Timeout süresini artır (varsayılan 5 saniye)
        g.db.engine.pool_timeout = 30
    return g.db 