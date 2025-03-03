from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.services.content_service import ContentService
from app.utils.validators import ValidationError
from app.forms.user_form import UserForm
from app.models import User
import asyncio

users_bp = Blueprint('users', __name__, url_prefix='/users')
content_service = ContentService()

@users_bp.route('/')
@login_required
def index():
    """Kullanıcı listesi sayfası"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Kullanıcıları getir - senkron olarak çalışacak şekilde düzenlendi
    try:
        # ContentService asenkron olduğundan, doğrudan firestore'a erişim yapalım
        users = []  # Boş bir kullanıcı listesi başlat
        
        # Firebase bağlantısını kullanarak kullanıcıları al
        from app import db
        user_docs = db.collection('users').limit(per_page).get()
        
        for doc in user_docs:
            user_data = doc.to_dict()
            user_data['id'] = doc.id  # ID'yi ekleyelim
            users.append(user_data)
            
        return render_template('users/index.html', users=users)
    except Exception as e:
        flash(f'Kullanıcılar getirilirken bir hata oluştu: {str(e)}', 'error')
        return render_template('users/index.html', users=[])

@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Yeni kullanıcı oluşturma sayfası"""
    form = UserForm()
    
    if form.validate_on_submit():
        try:
            # Kullanıcı verilerini hazırla
            user_data = {
                'username': form.username.data,
                'email': form.email.data,
                'password': form.password.data,
                'role': form.role.data,
                'is_active': form.is_active.data
            }
            
            # Kullanıcıyı oluştur
            user_id = content_service.create_content('users', user_data)
            
            if user_id:
                flash('Kullanıcı başarıyla oluşturuldu.', 'success')
                return redirect(url_for('users.index'))
            else:
                flash('Kullanıcı oluşturulurken bir hata oluştu.', 'error')
        
        except ValidationError as e:
            flash(str(e), 'error')
    
    return render_template('users/form.html', form=form)

@users_bp.route('/<user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(user_id):
    """Kullanıcı düzenleme sayfası"""
    # Kullanıcıyı getir
    user = content_service.get_content('users', user_id)
    if not user:
        flash('Kullanıcı bulunamadı.', 'error')
        return redirect(url_for('users.index'))
    
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        try:
            # Kullanıcı verilerini hazırla
            user_data = {
                'username': form.username.data,
                'email': form.email.data,
                'role': form.role.data,
                'is_active': form.is_active.data
            }
            
            # Şifre değiştirilecekse ekle
            if form.password.data:
                user_data['password'] = form.password.data
            
            # Kullanıcıyı güncelle
            if content_service.update_content('users', user_id, user_data):
                flash('Kullanıcı başarıyla güncellendi.', 'success')
                return redirect(url_for('users.index'))
            else:
                flash('Kullanıcı güncellenirken bir hata oluştu.', 'error')
        
        except ValidationError as e:
            flash(str(e), 'error')
    
    return render_template('users/form.html', form=form, user=user)

@users_bp.route('/<user_id>/delete', methods=['DELETE'])
@login_required
def delete(user_id):
    """Kullanıcı silme endpoint'i"""
    try:
        # Kullanıcıyı getir
        user = content_service.get_content('users', user_id)
        if not user:
            return jsonify({'error': 'Kullanıcı bulunamadı.'}), 404
        
        # Kendini silmeye çalışıyorsa engelle
        if user_id == current_user.id:
            return jsonify({'error': 'Kendi hesabınızı silemezsiniz.'}), 400
        
        # Kullanıcıyı sil
        if content_service.delete_content('users', user_id):
            return jsonify({'message': 'Kullanıcı başarıyla silindi.'}), 200
        else:
            return jsonify({'error': 'Kullanıcı silinirken bir hata oluştu.'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500 