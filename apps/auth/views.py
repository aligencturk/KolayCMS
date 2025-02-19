from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from apps.models import User, db
import traceback
from datetime import datetime

auth_bp = Blueprint('auth', __name__, template_folder='templates')

@auth_bp.route('/')
def index():
    current_app.logger.info('Auth ana sayfa isteği alındı')
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        current_app.logger.debug('Login sayfası istendi')
        # Zaten giriş yapmış kullanıcıları yönlendir
        if current_user.is_authenticated:
            current_app.logger.debug(f'Kullanıcı zaten giriş yapmış: {current_user.username}')
            if current_user.role == 'admin':
                return redirect(url_for('admin.index'))
            return redirect(url_for('main.index'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            remember = request.form.get('remember', False)
            
            current_app.logger.debug(f'Login denemesi: {username}')
            
            if not username or not password:
                flash('Kullanıcı adı ve şifre gereklidir.', 'error')
                return render_template('auth/login.html')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                if not user.is_active:
                    current_app.logger.warning(f'Pasif hesap girişi denemesi: {username}')
                    flash('Hesabınız aktif değil. Lütfen yönetici ile iletişime geçin.', 'error')
                    return redirect(url_for('auth.login'))
                    
                login_user(user, remember=remember)
                user.last_login = datetime.now()
                db.session.commit()
                
                current_app.logger.info(f'Başarılı giriş: {username}')
                
                # Yönlendirme için next parametresini kontrol et
                next_page = request.args.get('next')
                if not next_page or not next_page.startswith('/'):
                    next_page = url_for('admin.index')
                
                return redirect(next_page)
            
            current_app.logger.warning(f'Başarısız giriş denemesi: {username}')
            flash('Kullanıcı adı veya şifre hatalı!', 'error')
            
        return render_template('auth/login.html')
        
    except Exception as e:
        current_app.logger.error(f'Login hatası: {str(e)}')
        flash('Bir hata oluştu. Lütfen tekrar deneyin.', 'error')
        return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    try:
        logout_user()
        flash('Başarıyla çıkış yaptınız.', 'success')
        return redirect(url_for('auth.login'))
    except Exception as e:
        flash('Çıkış yapılırken bir hata oluştu.', 'error')
        return redirect(url_for('admin.index')) 