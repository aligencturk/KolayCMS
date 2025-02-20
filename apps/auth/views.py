from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from apps.models import User, db
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired
import traceback
from datetime import datetime

auth_bp = Blueprint('auth', __name__, template_folder='templates')

class LoginForm(FlaskForm):
    username = StringField('Kullanıcı Adı', validators=[DataRequired()])
    password = PasswordField('Şifre', validators=[DataRequired()])

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
            
        form = LoginForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            
            current_app.logger.debug(f'Login denemesi: {username}')
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                if not user.is_active:
                    current_app.logger.warning(f'Pasif hesap girişi denemesi: {username}')
                    flash('Hesabınız aktif değil. Lütfen yönetici ile iletişime geçin.', 'error')
                    return redirect(url_for('auth.login'))
                    
                login_user(user)
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
            
        return render_template('auth/login.html', form=form)
        
    except Exception as e:
        current_app.logger.error(f'Login hatası: {str(e)}')
        flash('Bir hata oluştu. Lütfen tekrar deneyin.', 'error')
        return render_template('auth/login.html', form=form)

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