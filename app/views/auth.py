from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.models import User
from app.services.user_service import get_user_by_email, create_user
from app import logger, db
import firebase_admin
from firebase_admin import auth as firebase_auth
import pyrebase
import os
import json
from datetime import datetime

# Firebase yapılandırması
cred_path = os.path.join(os.getcwd(), 'kolaycms-8c482-firebase-adminsdk-fbsvc-b881455bed.json')

# Servis hesabı dosyasını oku
try:
    with open(cred_path, 'r') as f:
        service_account = json.load(f)
        logger.debug("Servis hesabı dosyası başarıyla okundu")
except Exception as e:
    logger.error(f"Servis hesabı dosyası okuma hatası: {str(e)}")
    service_account = {}

firebase_config = {
    "apiKey": os.getenv('FIREBASE_API_KEY'),
    "authDomain": os.getenv('FIREBASE_AUTH_DOMAIN', 'kolaycms-8c482.firebaseapp.com'),
    "databaseURL": os.getenv('FIREBASE_DATABASE_URL', 'https://kolaycms-8c482.firebaseio.com'),
    "projectId": os.getenv('FIREBASE_PROJECT_ID', 'kolaycms-8c482'),
    "storageBucket": os.getenv('FIREBASE_STORAGE_BUCKET', 'kolaycms-8c482.appspot.com'),
    "messagingSenderId": os.getenv('FIREBASE_MESSAGING_SENDER_ID', '109435599963'),
    "appId": os.getenv('FIREBASE_APP_ID', '1:109435599963:web:5f9f9f9f9f9f9f9f9f9f9f'),
    "serviceAccount": service_account
}

try:
    # Pyrebase ile Firebase Auth başlat
    firebase = pyrebase.initialize_app(firebase_config)
    auth = firebase.auth()
    logger.debug("Pyrebase başarıyla başlatıldı")
except Exception as e:
    logger.error(f"Pyrebase başlatma hatası: {str(e)}", exc_info=True)
    auth = None

# Blueprint tanımla
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Giriş sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        if not email or not password:
            flash('E-posta ve şifre alanları zorunludur.', 'error')
            return render_template('auth/login.html')
        
        try:
            # Debug için giriş bilgilerini logla
            logger.debug(f"Giriş denemesi: E-posta: {email}, Şifre: {'*' * len(password)}")
            
            # Varsayılan admin kontrolü
            if email == "admin@kolaycms.com" and password == "admin123":
                logger.debug("Varsayılan admin bilgileri tespit edildi, varsayılan admin hesabı oluşturuluyor/güncelleniyor")
                return redirect(url_for('auth.create_default_admin'))
            
            # Firebase ile kimlik doğrulama
            user = auth.sign_in_with_email_and_password(email, password)
            logger.debug(f"Firebase auth başarılı: {user['localId']}")
            
            # Firestore'dan kullanıcı bilgilerini al
            user_doc = db.collection('users').document(user['localId']).get()
            
            if not user_doc.exists:
                logger.error(f"Kullanıcı Firestore'da bulunamadı: {user['localId']}")
                flash('Kullanıcı bilgileri bulunamadı.', 'error')
                return render_template('auth/login.html')
            
            user_data = user_doc.to_dict()
            logger.debug(f"Firestore kullanıcı verisi: {user_data}")
            
            # Rol kontrolü
            role = user_data.get('role', 'user')
            logger.debug(f"Kullanıcı rolü: {role}")
            
            # User nesnesini oluştur
            user_obj = User(
                uid=user['localId'],
                email=email,
                username=user_data.get('username', email.split('@')[0]),
                role=role
            )
            
            # Debug için rol kontrolü
            logger.debug(f"User objesi oluşturuldu - Role: {user_obj.role}, Is Admin: {user_obj.is_admin}")
            
            # Kullanıcıyı giriş yap
            login_user(user_obj, remember=remember)
            logger.info(f"Kullanıcı başarıyla giriş yaptı: {email} (Role: {role})")
            
            # Admin kontrolü ve yönlendirme
            if role == 'admin':
                logger.debug("Admin kullanıcısı tespit edildi, dashboard'a yönlendiriliyor")
                return redirect(url_for('main.dashboard'))
            else:
                logger.debug("Normal kullanıcı tespit edildi, dashboard'a yönlendiriliyor")
                return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            logger.error(f"Giriş hatası: {str(e)}", exc_info=True)
            error_message = str(e)
            
            if "INVALID_PASSWORD" in error_message:
                flash('Hatalı şifre girdiniz.', 'error')
            elif "EMAIL_NOT_FOUND" in error_message:
                flash('Bu e-posta adresi ile kayıtlı kullanıcı bulunamadı.', 'error')
            elif "INVALID_EMAIL" in error_message:
                flash('Geçersiz e-posta adresi.', 'error')
            elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_message:
                flash('Çok fazla başarısız deneme. Lütfen daha sonra tekrar deneyin.', 'error')
            else:
                flash('Giriş yapılamadı. Lütfen bilgilerinizi kontrol edin.', 'error')
            
            return render_template('auth/login.html')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Çıkış yap"""
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Kayıt sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username', email.split('@')[0])
        
        try:
            # Firebase Authentication'da kullanıcı oluştur
            user = auth.create_user_with_email_and_password(email, password)
            user_id = user['localId']
            
            # İlk kullanıcı kontrolü
            users_ref = db.collection('users')
            existing_users = list(users_ref.limit(1).stream())
            is_first_user = len(existing_users) == 0
            
            # Firestore'a kullanıcı verilerini kaydet
            user_data = {
                'email': email,
                'username': username,
                'role': 'admin' if is_first_user else 'user',  # İlk kullanıcı admin olsun
                'is_active': True,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            }
            
            # Firestore'a kaydet
            users_ref.document(user_id).set(user_data)
            logger.info(f"Kullanıcı başarıyla oluşturuldu: {email} (Role: {user_data['role']})")
            
            flash('Başarıyla kayıt oldunuz. Lütfen giriş yapın.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            logger.error(f"Kayıt hatası: {str(e)}")
            error_message = str(e)
            if "EMAIL_EXISTS" in error_message:
                flash('Bu e-posta adresi zaten kullanılıyor.', 'error')
            elif "WEAK_PASSWORD" in error_message:
                flash('Şifreniz çok zayıf. Lütfen daha güçlü bir şifre seçin.', 'error')
            elif "INVALID_EMAIL" in error_message:
                flash('Geçersiz e-posta adresi.', 'error')
            else:
                flash('Kayıt başarısız. Lütfen bilgilerinizi kontrol edin.', 'error')
    
    return render_template('auth/register.html')

@auth_bp.route('/create-default-admin')
def create_default_admin():
    """Varsayılan admin hesabını oluştur"""
    try:
        email = "admin@kolaycms.com"
        password = "admin123"
        username = "Admin"
        
        # Firebase Authentication'da kullanıcı oluştur
        try:
            user = auth.create_user_with_email_and_password(email, password)
            user_id = user['localId']
            logger.debug(f"Varsayılan admin kullanıcısı oluşturuldu: {user_id}")
        except Exception as e:
            error_message = str(e)
            logger.debug(f"Kullanıcı oluşturma hatası: {error_message}")
            
            if "EMAIL_EXISTS" in error_message:
                # Kullanıcı zaten varsa giriş yap
                user = auth.sign_in_with_email_and_password(email, password)
                user_id = user['localId']
                logger.debug(f"Mevcut admin kullanıcısına giriş yapıldı: {user_id}")
            else:
                raise e
        
        # Firestore'a kullanıcı verilerini kaydet
        user_data = {
            'email': email,
            'username': username,
            'role': 'admin',
            'is_active': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        # Firestore'a kaydet
        db.collection('users').document(user_id).set(user_data)
        logger.info(f"Varsayılan admin kullanıcısı oluşturuldu/güncellendi: {email}")
        
        # User nesnesini oluştur
        user_obj = User(
            uid=user_id,
            email=email,
            username=username,
            role='admin'
        )
        
        # Kullanıcıyı giriş yap
        login_user(user_obj, remember=True)
        
        flash('Varsayılan admin hesabı oluşturuldu ve giriş yapıldı.', 'success')
        return redirect(url_for('main.dashboard'))
        
    except Exception as e:
        logger.error(f"Varsayılan admin oluşturma hatası: {str(e)}", exc_info=True)
        flash(f'Varsayılan admin hesabı oluşturulurken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('auth.login')) 