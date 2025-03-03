from flask import Flask, render_template
from flask_login import LoginManager
from flask_babel import Babel
from flask_admin import Admin
from flask_wtf.csrf import CSRFProtect
from config import Config
import os
import firebase_admin
from firebase_admin import credentials, firestore
import json

# Flask-Login için login manager
login_manager = LoginManager()
# Flask-Babel için çoklu dil desteği
babel = Babel()
# Flask-Admin için admin panel
admin = Admin(name='KolayCMS', template_mode='bootstrap4')
# CSRF koruması
csrf = CSRFProtect()

db = None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Firebase başlatma
    if not firebase_admin._apps:
        # Önce çevre değişkeninden okumayı deneyelim
        if app.config.get('FIREBASE_CREDENTIALS_JSON'):
            try:
                cred_dict = json.loads(app.config.get('FIREBASE_CREDENTIALS_JSON'))
                cred = credentials.Certificate(cred_dict)
            except Exception as e:
                app.logger.error(f"Firebase kimlik bilgileri JSON formatından yüklenirken hata: {str(e)}")
                # Hata durumunda dosyadan okumayı deneyelim
                try:
                    cred = credentials.Certificate(app.config['FIREBASE_CREDENTIALS_PATH'])
                except Exception as e2:
                    app.logger.error(f"Firebase kimlik bilgileri dosyadan yüklenirken hata: {str(e2)}")
                    raise e2
        else:
            # Çevre değişkeni yoksa dosyadan oku
            try:
                cred = credentials.Certificate(app.config['FIREBASE_CREDENTIALS_PATH'])
            except Exception as e:
                app.logger.error(f"Firebase kimlik bilgileri dosyadan yüklenirken hata: {str(e)}")
                raise e
                
        firebase_admin.initialize_app(cred)
    global db
    db = firestore.client()
    
    # Flask-Login
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Bu sayfayı görüntülemek için giriş yapmalısınız.'
    login_manager.login_message_category = 'warning'
    
    babel.init_app(app)
    admin.init_app(app)
    
    # CSRF koruması
    csrf.init_app(app)
    
    # Ana blueprint'leri kaydet
    from app.views.main import main_bp
    from app.views.auth import auth_bp
    from app.views.users import users_bp
    from app.modules.reports.views import reports_bp
    from app.modules.sliders.views import sliders_bp
    from app.modules.corporate.views import corporate_bp
    from app.modules.team.views import team_bp
    from app.modules.hr.views import hr_bp
    from app.modules.services.views import services_bp
    from app.modules.projects.views import projects_bp
    from app.modules.user.views import user_bp
    
    # Tema ve şablon yönetimi için yeni blueprint'ler
    from app.modules.themes.views import themes_bp
    from app.modules.templates.views import templates_bp
    from app.modules.page_builder.views import page_builder_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(sliders_bp, url_prefix='/sliders')
    app.register_blueprint(corporate_bp, url_prefix='/corporate')
    app.register_blueprint(team_bp, url_prefix='/team')
    app.register_blueprint(hr_bp, url_prefix='/hr')
    app.register_blueprint(services_bp, url_prefix='/services')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(users_bp)
    app.register_blueprint(user_bp)
    
    # Yeni blueprint'leri kaydet
    app.register_blueprint(themes_bp, url_prefix='/themes')
    app.register_blueprint(templates_bp, url_prefix='/templates')
    app.register_blueprint(page_builder_bp, url_prefix='/page-builder')
    
    # Hata sayfalarını kaydet
    register_error_handlers(app)
    
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    from app.services.user_service import get_user_by_id
    user_data = get_user_by_id(user_id)
    if user_data:
        user = User(
            uid=user_id,
            email=user_data.get('email'),
            username=user_data.get('username'),
            role=user_data.get('role', 'user')
        )
        user.is_active = user_data.get('is_active', True)
        return user
    return None

def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
        
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500 