from flask import Flask, render_template, request, jsonify, redirect, url_for, send_from_directory
from flask_login import LoginManager
from flask_babel import Babel
from flask_admin import Admin
from flask_wtf.csrf import CSRFProtect, generate_csrf
import os
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app, storage
import json
import logging
import sys
from dotenv import load_dotenv
from google.cloud import firestore

# .env dosyasını yükle
load_dotenv()

# Logging ayarları
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Flask-Login için login manager
login_manager = LoginManager()
# Flask-Babel için çoklu dil desteği
babel = Babel()
# Flask-Admin için admin panel
admin = Admin(name='KolayCMS', template_mode='bootstrap4')
# CSRF koruması
csrf = CSRFProtect()

# Global Firestore client
db = None

def init_firebase(app):
    """Firebase'i başlat"""
    global db
    try:
        logger.debug("Firebase başlatılıyor...")
        
        # Servis hesabı dosyasını kullan
        cred_path = os.path.join(os.getcwd(), 'kolaycms-8c482-firebase-adminsdk-fbsvc-b881455bed.json')
        
        if os.path.exists(cred_path):
            logger.debug(f"Servis hesabı dosyası bulundu: {cred_path}")
            
            # Firebase Admin SDK'yı başlat
            cred = credentials.Certificate(cred_path)
            try:
                firebase_admin.initialize_app(cred)
            except ValueError:
                logger.debug("Firebase zaten başlatılmış, yeni bir uygulama oluşturuluyor...")
                # Mevcut uygulamayı sil
                for app in firebase_admin._apps.values():
                    firebase_admin.delete_app(app)
                # Yeni uygulama oluştur
                firebase_admin.initialize_app(cred)
            
            # Firestore istemcisini al
            db = firebase_admin.firestore.client()
            logger.debug("Firebase başarıyla başlatıldı")
            return db
        else:
            logger.error(f"Servis hesabı dosyası bulunamadı: {cred_path}")
            raise FileNotFoundError(f"Servis hesabı dosyası bulunamadı: {cred_path}")
            
    except Exception as e:
        logger.error(f"Firebase başlatma hatası: {str(e)}")
        raise

def create_app(config_name='default'):
    """Flask uygulamasını oluştur ve yapılandır"""
    try:
        app = Flask(__name__, 
                    static_folder='static',
                    static_url_path='/static')
        
        # Tema ve geçici klasörleri oluştur
        themes_dir = os.path.join(os.path.dirname(app.root_path), 'themes')
        temp_dir = os.path.join(os.path.dirname(app.root_path), 'temp')
        
        if not os.path.exists(themes_dir):
            try:
                os.makedirs(themes_dir, exist_ok=True)
                logger.info(f"themes dizini oluşturuldu: {os.path.abspath(themes_dir)}")
            except Exception as e:
                logger.error(f"themes dizini oluşturulurken hata: {str(e)}")
        
        if not os.path.exists(temp_dir):
            try:
                os.makedirs(temp_dir, exist_ok=True)
                logger.info(f"temp dizini oluşturuldu: {os.path.abspath(temp_dir)}")
            except Exception as e:
                logger.error(f"temp dizini oluşturulurken hata: {str(e)}")
        
        # Debug modu aktif
        app.config['DEBUG'] = True
        app.config['TESTING'] = True
        app.config['FLASK_DEBUG'] = True
        
        # Konfigürasyonu yükle
        from app.config import config
        app.config.from_object(config[config_name] if config_name else 'default')
        app.config['WTF_CSRF_ENABLED'] = True
        app.config['WTF_CSRF_SECRET_KEY'] = app.config['SECRET_KEY']
        app.config['WTF_CSRF_TIME_LIMIT'] = None
        
        # Tema dizinini static folder olarak ekle
        if os.path.exists(app.config['THEMES_STATIC_FOLDER']):
            app.static_folder = app.config['THEMES_STATIC_FOLDER']
            logger.debug(f"Tema static dizini ayarlandı: {app.static_folder}")
        
        # CSRF korumasını başlat
        csrf.init_app(app)
        
        # CSRF token'ı tüm şablonlara ekle
        @app.context_processor
        def inject_csrf_token():
            return dict(csrf_token=generate_csrf())
        
        # Şablonlara now değişkenini ekle
        @app.context_processor
        def inject_now():
            """Şablon değişkenlerini ekle"""
            from datetime import datetime
            current_time = datetime.utcnow()
            return {
                'now': current_time  # Artık çağrılabilir bir fonksiyon değil, doğrudan bir datetime nesnesi
            }
        
        # Datetime filtresi ekle
        @app.template_filter('datetime')
        def format_datetime(value, format='%d.%m.%Y %H:%M'):
            """Tarih değerini biçimlendirir."""
            if value is None:
                return ""
            
            # Eğer zaten datetime nesnesi ise doğrudan kullan
            from datetime import datetime
            if isinstance(value, datetime):
                return value.strftime(format)
            
            # String ise dönüştürmeyi dene
            if isinstance(value, str):
                try:
                    # RFC 2822 formatını dene
                    value = datetime.strptime(value, '%a, %d %b %Y %H:%M:%S GMT')
                    return value.strftime(format)
                except ValueError:
                    try:
                        # ISO format dene
                        value = datetime.fromisoformat(value.replace('Z', '+00:00'))
                        return value.strftime(format)
                    except ValueError:
                        pass
                    
            # Diğer durumlarda orijinal değeri döndür
            return str(value)
        
        # Now tag'i ekle ({{ now_tag('Y') }} kullanımı için)
        def now_tag(format_string='%Y'):
            """Geçerli tarih/saati biçimlendirir. Örnek: {{ now_tag('Y') }} -> 2023"""
            from datetime import datetime
            return datetime.utcnow().strftime(format_string)
        
        # get_now fonksiyonu
        def get_now():
            """Geçerli tarih/saati döndürür. Şablonlarda {{ get_now() }} olarak çağrılabilir."""
            from datetime import datetime
            return datetime.utcnow()
        
        # Jinja2 global fonksiyonları tanımla
        app.jinja_env.globals.update(now_tag=now_tag, get_now=get_now)
        
        # Ana sayfa yönlendirmesi
        @app.route('/')
        def index():
            return redirect(url_for('main.dashboard'))
        
        # Hata sayfaları
        @app.errorhandler(400)
        def bad_request_error(error):
            logger.error(f"400 hatası: {str(error)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': str(error)}), 400
            return render_template('errors/400.html', error=error), 400
        
        @app.errorhandler(500)
        def internal_server_error(error):
            logger.error(f"500 hatası: {str(error)}", exc_info=True)
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'error': str(error)}), 500
            return render_template('errors/500.html', error=error), 500
        
        # Firebase'i başlat
        global db
        db = init_firebase(app)
        
        # Flask-Login
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'
        login_manager.login_message = None
        login_manager.login_message_category = 'warning'
        
        # Diğer uzantıları başlat
        babel.init_app(app)
        admin.init_app(app)
        
        # Blueprint'leri kaydet
        register_blueprints(app)
        
        # Tema HTML sayfa isteklerini yakalayıp doğru adrese yönlendir
        @app.route('/<page_file>.html')
        def theme_html_redirect(page_file):
            """HTML dosya isteklerini doğru tema sayfasına yönlendir"""
            # Referer'dan tema ID'sini al
            referer = request.headers.get('Referer', '')
            theme_id = None
            
            # Referer'dan tema ID'sini çözümle
            if 'theme_id=' in referer:
                theme_id = referer.split('theme_id=')[1].split('&')[0]
                logger.debug(f"Referer'dan tema ID bulundu: {theme_id}")
            
            # Tema ID yoksa session'dan bulmaya çalış
            if not theme_id and 'current_theme_id' in request.cookies:
                theme_id = request.cookies.get('current_theme_id')
                logger.debug(f"Cookie'den tema ID bulundu: {theme_id}")
            
            # Tema ID yoksa veritabanından aktif temayı al
            if not theme_id:
                try:
                    # Aktif temayı bul
                    active_theme_ref = db.collection('themes').where('is_active', '==', True).limit(1).stream()
                    active_themes = list(active_theme_ref)
                    
                    if active_themes:
                        theme_id = active_themes[0].id
                        logger.debug(f"Veritabanından aktif tema ID bulundu: {theme_id}")
                except Exception as e:
                    logger.error(f"Aktif tema sorgulanırken hata: {str(e)}")
            
            if not theme_id:
                logger.error(f"HTML yönlendirme için tema ID bulunamadı: {page_file}.html")
                return render_template('errors/404.html'), 404
            
            # Sayfa türüne göre doğru URL'ye yönlendir
            if page_file == 'index':
                return redirect(url_for('themes.view_website', theme_id=theme_id))
            elif page_file == 'services':
                return redirect(url_for('themes.view_services', theme_id=theme_id))
            elif page_file == 'about':
                return redirect(url_for('themes.view_about', theme_id=theme_id))
            elif page_file == 'blog':
                return redirect(url_for('themes.view_blog', theme_id=theme_id))
            elif page_file == 'events':
                return redirect(url_for('themes.view_events', theme_id=theme_id))
            elif page_file == 'contact':
                return redirect(url_for('themes.view_contact', theme_id=theme_id))
            else:
                # Bilinmeyen sayfalar için tema sayfa fonksiyonuna yönlendir
                return redirect(url_for('themes.theme_page', theme_id=theme_id, page_name=page_file))
                
        # Tema içindeki diğer dosyalar için yönlendirme (css, js, images)
        @app.route('/css/<path:filename>')
        def theme_css_redirect(filename):
            """CSS isteklerini doğru tema CSS dosyalarına yönlendir"""
            theme_id = request.cookies.get('current_theme_id')
            
            if not theme_id:
                # Referer'dan tema ID'sini al
                referer = request.headers.get('Referer', '')
                if 'theme_id=' in referer:
                    theme_id = referer.split('theme_id=')[1].split('&')[0]
            
            if not theme_id:
                # Aktif temayı bul
                try:
                    active_theme_ref = db.collection('themes').where('is_active', '==', True).limit(1).stream()
                    active_themes = list(active_theme_ref)
                    if active_themes:
                        theme_id = active_themes[0].id
                except Exception as e:
                    logger.error(f"CSS yönlendirme için aktif tema sorgulanırken hata: {str(e)}")
            
            if theme_id:
                css_path = os.path.join(os.getcwd(), 'themes', theme_id, 'static', 'css', filename)
                if os.path.exists(css_path):
                    return send_from_directory(os.path.join(os.getcwd(), 'themes', theme_id, 'static', 'css'), filename)
            
            # Varsayılan CSS döndür
            logger.warning(f"CSS dosyası bulunamadı, boş CSS döndürülüyor: {filename}")
            return app.response_class(
                response="/* CSS dosyası bulunamadı */",
                status=200,
                mimetype='text/css'
            )
            
        @app.route('/js/<path:filename>')
        def theme_js_redirect(filename):
            """JS isteklerini doğru tema JS dosyalarına yönlendir"""
            theme_id = request.cookies.get('current_theme_id')
            
            if not theme_id:
                # Referer'dan tema ID'sini al
                referer = request.headers.get('Referer', '')
                if 'theme_id=' in referer:
                    theme_id = referer.split('theme_id=')[1].split('&')[0]
            
            if not theme_id:
                # Aktif temayı bul
                try:
                    active_theme_ref = db.collection('themes').where('is_active', '==', True).limit(1).stream()
                    active_themes = list(active_theme_ref)
                    if active_themes:
                        theme_id = active_themes[0].id
                except Exception as e:
                    logger.error(f"JS yönlendirme için aktif tema sorgulanırken hata: {str(e)}")
            
            if theme_id:
                js_path = os.path.join(os.getcwd(), 'themes', theme_id, 'static', 'js', filename)
                if os.path.exists(js_path):
                    return send_from_directory(os.path.join(os.getcwd(), 'themes', theme_id, 'static', 'js'), filename)
            
            # Varsayılan JS döndür
            logger.warning(f"JS dosyası bulunamadı, boş JS döndürülüyor: {filename}")
            return app.response_class(
                response="/* JavaScript dosyası bulunamadı */",
                status=200,
                mimetype='application/javascript'
            )
            
        @app.route('/images/<path:filename>')
        def theme_images_redirect(filename):
            """Resim isteklerini doğru tema resim dosyalarına yönlendir"""
            theme_id = request.cookies.get('current_theme_id')
            
            if not theme_id:
                # Referer'dan tema ID'sini al
                referer = request.headers.get('Referer', '')
                if 'theme_id=' in referer:
                    theme_id = referer.split('theme_id=')[1].split('&')[0]
            
            if not theme_id:
                # Aktif temayı bul
                try:
                    active_theme_ref = db.collection('themes').where('is_active', '==', True).limit(1).stream()
                    active_themes = list(active_theme_ref)
                    if active_themes:
                        theme_id = active_themes[0].id
                except Exception as e:
                    logger.error(f"Resim yönlendirme için aktif tema sorgulanırken hata: {str(e)}")
            
            if theme_id:
                image_path = os.path.join(os.getcwd(), 'themes', theme_id, 'static', 'images', filename)
                if os.path.exists(image_path):
                    return send_from_directory(os.path.join(os.getcwd(), 'themes', theme_id, 'static', 'images'), filename)
            
            # Varsayılan resim döndür
            logger.warning(f"Resim dosyası bulunamadı, varsayılan resim döndürülüyor: {filename}")
            return app.send_static_file('images/default.png')
                
        # Tema statik dosyaları için basitleştirilmiş URL kuralları
        @app.route('/themes/css/<path:filename>')
        def simple_theme_css(filename):
            """Basit tema CSS dosyalarını servis et (aktif temadan)"""
            try:
                # Aktif temayı bul
                active_theme_ref = db.collection('themes').where('is_active', '==', True).limit(1).stream()
                active_themes = list(active_theme_ref)
                
                if not active_themes:
                    logger.error("Aktif tema bulunamadı")
                    return app.response_class(
                        response="/* CSS dosyası bulunamadı - aktif tema yok */",
                        status=200,
                        mimetype='text/css'
                    )
                
                theme_id = active_themes[0].id
                theme_css_dir = os.path.join(os.getcwd(), 'themes', theme_id, 'static', 'css')
                
                if os.path.exists(os.path.join(theme_css_dir, filename)):
                    logger.debug(f"Simple CSS dosyası servis ediliyor: {filename}, aktif tema: {theme_id}")
                    return send_from_directory(theme_css_dir, filename)
                else:
                    logger.error(f"CSS dosyası bulunamadı: {filename}")
                    return app.response_class(
                        response=f"/* CSS dosyası bulunamadı: {filename} */",
                        status=200,
                        mimetype='text/css'
                    )
                
            except Exception as e:
                logger.error(f"Simple theme CSS hatası: {str(e)}")
                return app.response_class(
                    response=f"/* CSS dosyası sunulurken hata: {str(e)} */",
                    status=200, 
                    mimetype='text/css'
                )
        
        @app.route('/themes/js/<path:filename>')
        def simple_theme_js(filename):
            """Basit tema JS dosyalarını servis et (aktif temadan)"""
            try:
                # Aktif temayı bul
                active_theme_ref = db.collection('themes').where('is_active', '==', True).limit(1).stream()
                active_themes = list(active_theme_ref)
                
                if not active_themes:
                    logger.error("Aktif tema bulunamadı")
                    return app.response_class(
                        response="/* JS dosyası bulunamadı - aktif tema yok */",
                        status=200,
                        mimetype='application/javascript'
                    )
                
                theme_id = active_themes[0].id
                theme_js_dir = os.path.join(os.getcwd(), 'themes', theme_id, 'static', 'js')
                
                if os.path.exists(os.path.join(theme_js_dir, filename)):
                    logger.debug(f"Simple JS dosyası servis ediliyor: {filename}, aktif tema: {theme_id}")
                    return send_from_directory(theme_js_dir, filename)
                else:
                    logger.error(f"JS dosyası bulunamadı: {filename}")
                    return app.response_class(
                        response=f"/* JS dosyası bulunamadı: {filename} */",
                        status=200,
                        mimetype='application/javascript'
                    )
                
            except Exception as e:
                logger.error(f"Simple theme JS hatası: {str(e)}")
                return app.response_class(
                    response=f"/* JS dosyası sunulurken hata: {str(e)} */",
                    status=200, 
                    mimetype='application/javascript'
                )
        
        @app.route('/themes/images/<path:filename>')
        def simple_theme_images(filename):
            """Basit tema resim dosyalarını servis et (aktif temadan)"""
            try:
                # Aktif temayı bul
                active_theme_ref = db.collection('themes').where('is_active', '==', True).limit(1).stream()
                active_themes = list(active_theme_ref)
                
                if not active_themes:
                    logger.error("Aktif tema bulunamadı")
                    return app.send_static_file('images/default.png')
                
                theme_id = active_themes[0].id
                theme_img_dir = os.path.join(os.getcwd(), 'themes', theme_id, 'static', 'images')
                
                if os.path.exists(os.path.join(theme_img_dir, filename)):
                    logger.debug(f"Simple resim dosyası servis ediliyor: {filename}, aktif tema: {theme_id}")
                    return send_from_directory(theme_img_dir, filename)
                else:
                    logger.error(f"Resim dosyası bulunamadı: {filename}")
                    return app.send_static_file('images/default.png')
                
            except Exception as e:
                logger.error(f"Simple theme resim hatası: {str(e)}")
                return app.send_static_file('images/default.png')
        
        logger.info("Uygulama başarıyla başlatıldı")
        return app
    except Exception as e:
        logger.error(f"Uygulama başlatma hatası: {str(e)}")
        raise

def register_blueprints(app):
    """Blueprint'leri kaydet"""
    try:
        logger.debug("Blueprint'ler kaydediliyor...")
        
        # CMS Blueprint'leri
        from app.views.main import main_bp
        from app.views.auth import auth_bp
        from app.modules.reports.views import reports_bp
        from app.modules.sliders.views import sliders_bp
        from app.modules.corporate.views import corporate_bp
        from app.modules.team.views import team_bp
        from app.views.components import components_bp
        from app.views.blog import bp as blog_bp
        from app.modules.menus.views import menus_bp
        from app.modules.themes.views import themes_bp
        
        app.register_blueprint(main_bp)  # Ana blueprint
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(reports_bp)  # URL öneki kaldırıldı
        app.register_blueprint(sliders_bp, url_prefix='/sliders')
        app.register_blueprint(corporate_bp, url_prefix='/corporate')
        app.register_blueprint(team_bp, url_prefix='/team')
        app.register_blueprint(components_bp)
        app.register_blueprint(blog_bp)
        app.register_blueprint(menus_bp)
        app.register_blueprint(themes_bp, url_prefix='/themes')
        
        logger.debug("Blueprint'ler başarıyla kaydedildi")
    except Exception as e:
        logger.error(f"Blueprint kayıt hatası: {str(e)}")
        raise

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    try:
        # Firebase Auth'dan kullanıcı bilgilerini al
        user = firebase_admin.auth.get_user(user_id)
        if user:
            # Firestore'dan kullanıcı verilerini al
            user_doc = db.collection('users').document(user.uid).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                logger.debug(f"Kullanıcı verisi yüklendi - ID: {user.uid}, Role: {user_data.get('role', 'user')}")
                return User(
                    uid=user.uid,
                    email=user.email,
                    username=user_data.get('username', user.email.split('@')[0]),
                    role=user_data.get('role', 'user')
                )
            else:
                logger.warning(f"Kullanıcı Firestore'da bulunamadı: {user.uid}")
    except Exception as e:
        logger.error(f"Kullanıcı yükleme hatası: {str(e)}")
    return None

def register_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
        
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500 