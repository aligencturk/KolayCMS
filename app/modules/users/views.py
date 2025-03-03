from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.modules.users.models import UserModule

users_bp = Blueprint('users', __name__, url_prefix='/users')
user_module = UserModule()

@users_bp.route('/')
@login_required
def index():
    """Kullanıcı listesi"""
    page = request.args.get('page', 1, type=int)
    limit = 10
    users = user_module.list(limit=limit)
    return render_template('users/index.html', users=users)

@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Yeni kullanıcı oluştur"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role', 'user')
        
        if not username or not email:
            flash('Kullanıcı adı ve email zorunludur.', 'error')
        else:
            try:
                user_id = user_module.create_user(username, email, role)
                flash('Kullanıcı başarıyla oluşturuldu.', 'success')
                return redirect(url_for('users.index'))
            except Exception as e:
                flash(f'Hata oluştu: {str(e)}', 'error')
    
    return render_template('users/create.html')

@users_bp.route('/<user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    """Kullanıcı düzenle"""
    user = user_module.get(user_id)
    if not user:
        flash('Kullanıcı bulunamadı.', 'error')
        return redirect(url_for('users.index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        role = request.form.get('role')
        
        if not username or not email:
            flash('Kullanıcı adı ve email zorunludur.', 'error')
        else:
            try:
                user_module.update(user_id, {
                    'username': username,
                    'email': email,
                    'role': role
                })
                flash('Kullanıcı başarıyla güncellendi.', 'success')
                return redirect(url_for('users.index'))
            except Exception as e:
                flash(f'Hata oluştu: {str(e)}', 'error')
    
    return render_template('users/edit.html', user=user)

@users_bp.route('/<user_id>/delete', methods=['POST'])
@login_required
def delete(user_id):
    """Kullanıcı sil"""
    try:
        if user_module.delete(user_id):
            flash('Kullanıcı başarıyla silindi.', 'success')
        else:
            flash('Kullanıcı bulunamadı.', 'error')
    except Exception as e:
        flash(f'Hata oluştu: {str(e)}', 'error')
    
    return redirect(url_for('users.index')) 