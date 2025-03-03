from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.forms.auth_form import LoginForm, RegisterForm
from app.modules.user.models import UserModule
from firebase_admin import auth as firebase_auth
import firebase_admin.exceptions
import requests
import json
import logging

# Blueprint tanımı
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
user_module = UserModule()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Kullanıcı giriş sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        
        try:
            # Debug: İstek öncesi bilgileri yazdır
            print("=================================================")
            print(f"GİRİŞ İŞLEMİ: {email} kullanıcısı için giriş denemesi")
            
            # Firebase Authentication REST API ile giriş yap
            firebase_api_key = current_app.config['FIREBASE_API_KEY']
            print(f"Kullanılan API anahtarı: {firebase_api_key}")
            
            # Her iki endpoint'i de test edelim
            auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={firebase_api_key}"
            print(f"İstek URL: {auth_url}")
            
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            # Debug: Payload'ı yazdır (şifre hariç)
            debug_payload = payload.copy()
            debug_payload['password'] = '********'
            print(f"Gönderilen veriler: {json.dumps(debug_payload)}")
            
            # İsteği gönder
            response = requests.post(auth_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
            
            # Yanıtı analiz et
            print(f"Yanıt durum kodu: {response.status_code}")
            print(f"Yanıt içeriği: {response.text}")
            
            if response.status_code != 200:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Bilinmeyen hata')
                print(f"Hata mesajı: {error_message}")
                
                if error_message == 'INVALID_PASSWORD' or error_message == 'EMAIL_NOT_FOUND':
                    flash('Giriş başarısız. E-posta veya şifre hatalı.', 'danger')
                else:
                    flash(f'Giriş başarısız: {error_message}', 'danger')
                return render_template('auth/login.html', form=form)
            
            # Başarılı giriş
            auth_data = response.json()
            user_id = auth_data['localId']
            print(f"Başarılı giriş. Kullanıcı ID: {user_id}")
            
            # Kullanıcı Firestore'da var mı kontrol et
            user = user_module.get_user_by_id(user_id)
            
            if not user:
                print(f"Kullanıcı Firestore'da bulunamadı, oluşturuluyor...")
                # Kullanıcı Firestore'da yoksa oluştur
                user_record = firebase_auth.get_user(user_id)
                user = user_module.create_user_with_id(
                    uid=user_id,
                    email=email,
                    username=user_record.display_name or email.split('@')[0],
                    role='user'
                )
            
            # Kullanıcı aktif değilse giriş yapmasına izin verme
            if not user.is_active:
                print(f"Kullanıcı aktif değil. Giriş reddedildi.")
                flash('Hesabınız devre dışı bırakılmıştır. Lütfen yönetici ile iletişime geçin.', 'danger')
                return render_template('auth/login.html', form=form)
            
            # Kullanıcıyı giriş yap
            print(f"Kullanıcı giriş yapıyor...")
            login_user(user, remember=form.remember.data)
            print(f"Giriş başarılı. Yönlendiriliyor...")
            
            # Yönlendirme
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            print(f"Giriş sırasında hata: {str(e)}")
            print("=================================================")
            flash(f'Giriş başarısız: {str(e)}', 'danger')
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Kullanıcı kayıt sayfası"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        username = form.username.data
        
        try:
            # Debug: İstek öncesi bilgileri yazdır
            print("=================================================")
            print(f"KAYIT İŞLEMİ: {email} kullanıcısı için kayıt denemesi")
            
            # Firebase Authentication REST API ile kayıt ol
            firebase_api_key = current_app.config['FIREBASE_API_KEY']
            print(f"Kullanılan API anahtarı: {firebase_api_key}")
            
            auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={firebase_api_key}"
            print(f"İstek URL: {auth_url}")
            
            payload = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            # Debug: Payload'ı yazdır (şifre hariç)
            debug_payload = payload.copy()
            debug_payload['password'] = '********'
            print(f"Gönderilen veriler: {json.dumps(debug_payload)}")
            
            # İsteği gönder
            response = requests.post(auth_url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
            
            # Yanıtı analiz et
            print(f"Yanıt durum kodu: {response.status_code}")
            print(f"Yanıt içeriği: {response.text}")
            
            if response.status_code != 200:
                error_data = response.json()
                error_message = error_data.get('error', {}).get('message', 'Bilinmeyen hata')
                print(f"Hata mesajı: {error_message}")
                
                if error_message == 'EMAIL_EXISTS':
                    flash('Bu e-posta adresi zaten kullanılıyor.', 'danger')
                else:
                    flash(f'Kayıt sırasında bir hata oluştu: {error_message}', 'danger')
                return render_template('auth/register.html', form=form)
            
            # Başarılı kayıt
            auth_data = response.json()
            user_id = auth_data['localId']
            print(f"Başarılı kayıt. Kullanıcı ID: {user_id}")
            
            # Kullanıcıyı Firestore'a kaydet
            user = user_module.create_user_with_id(
                uid=user_id,
                email=email,
                username=username,
                role='user'
            )
            print(f"Kullanıcı Firestore'a kaydedildi.")
            
            flash('Hesabınız başarıyla oluşturuldu. Şimdi giriş yapabilirsiniz.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            print(f"Kayıt sırasında hata: {str(e)}")
            print("=================================================")
            flash(f'Kayıt sırasında bir hata oluştu: {str(e)}', 'danger')
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    """Kullanıcı çıkış işlemi"""
    logout_user()
    flash('Başarıyla çıkış yaptınız.', 'success')
    return redirect(url_for('auth.login')) 