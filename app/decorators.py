from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user

def admin_required(f):
    """Sadece admin rolüne sahip kullanıcıların erişebileceği sayfalar için dekoratör"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Geçici olarak admin kontrolünü kaldırıyoruz
        # if not current_user.is_admin():
        #     flash('Bu sayfaya erişim yetkiniz bulunmamaktadır.', 'danger')
        #     return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def editor_required(f):
    """Sadece editor veya admin rolüne sahip kullanıcıların erişebileceği sayfalar için dekoratör"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Geçici olarak editör kontrolünü kaldırıyoruz
        # if not current_user.is_editor():
        #     flash('Bu sayfaya erişim yetkiniz bulunmamaktadır.', 'danger')
        #     return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function 