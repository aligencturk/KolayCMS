from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from app import logger

def admin_required(f):
    """Sadece admin rolüne sahip kullanıcıların erişebileceği sayfalar için dekoratör"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.debug(f"Admin kontrolü - User: {current_user.email}, Role: {current_user.role}")
        if not current_user.role == 'admin':
            logger.warning(f"Yetkisiz erişim denemesi - User: {current_user.email}, Role: {current_user.role}")
            flash('Bu sayfaya erişim yetkiniz bulunmamaktadır.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def editor_required(f):
    """Sadece editor veya admin rolüne sahip kullanıcıların erişebileceği sayfalar için dekoratör"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.debug(f"Editor kontrolü - User: {current_user.email}, Role: {current_user.role}")
        if not (current_user.role == 'editor' or current_user.role == 'admin'):
            logger.warning(f"Yetkisiz erişim denemesi - User: {current_user.email}, Role: {current_user.role}")
            flash('Bu sayfaya erişim yetkiniz bulunmamaktadır.', 'danger')
            return redirect(url_for('main.dashboard'))
        return f(*args, **kwargs)
    return decorated_function 