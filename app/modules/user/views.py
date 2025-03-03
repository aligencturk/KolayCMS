from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.modules.user.models import UserModule
from app.forms.user_form import UserForm, PasswordChangeForm
from app.decorators import admin_required
import math

user_bp = Blueprint('user', __name__, url_prefix='/users')
user_module = UserModule()

@user_bp.route('/')
@login_required
@admin_required
def index():
    """Kullanıcı listesi sayfası"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    users = user_module.get_all_users()
    total_users = len(users)
    
    # Sayfalama
    total_pages = math.ceil(total_users / per_page)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    paginated_users = users[start_idx:end_idx]
    
    return render_template(
        'user/index.html',
        users=paginated_users,
        page=page,
        total_pages=total_pages,
        total_users=total_users
    )

@user_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Yeni kullanıcı oluşturma sayfası"""
    form = UserForm()
    
    if form.validate_on_submit():
        try:
            # Kullanıcı e-posta kontrolü
            existing_user = user_module.get_user_by_email(form.email.data)
            if existing_user:
                flash('Bu e-posta adresi zaten kullanılıyor.', 'danger')
                return render_template('user/form.html', form=form, title='Yeni Kullanıcı')
            
            # Yeni kullanıcı oluştur
            user_module.create_user(
                email=form.email.data,
                password=form.password.data,
                username=form.username.data,
                role=form.role.data
            )
            
            flash('Kullanıcı başarıyla oluşturuldu.', 'success')
            return redirect(url_for('user.index'))
            
        except Exception as e:
            flash(f'Kullanıcı oluşturulurken bir hata oluştu: {str(e)}', 'danger')
    
    return render_template('user/form.html', form=form, title='Yeni Kullanıcı')

@user_bp.route('/edit/<user_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(user_id):
    """Kullanıcı düzenleme sayfası"""
    user = user_module.get_user_by_id(user_id)
    if not user:
        flash('Kullanıcı bulunamadı.', 'danger')
        return redirect(url_for('user.index'))
    
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        try:
            # E-posta değişikliği kontrolü
            if form.email.data != user.email:
                existing_user = user_module.get_user_by_email(form.email.data)
                if existing_user:
                    flash('Bu e-posta adresi zaten kullanılıyor.', 'danger')
                    return render_template('user/form.html', form=form, title='Kullanıcı Düzenle', user=user)
            
            # Kullanıcı bilgilerini güncelle
            update_data = {
                'username': form.username.data,
                'email': form.email.data,
                'role': form.role.data,
                'is_active': form.is_active.data
            }
            
            user_module.update_user(user_id, update_data)
            
            # Şifre değişikliği varsa güncelle
            if form.password.data:
                user_module.change_password(user_id, form.password.data)
            
            flash('Kullanıcı bilgileri başarıyla güncellendi.', 'success')
            return redirect(url_for('user.index'))
            
        except Exception as e:
            flash(f'Kullanıcı güncellenirken bir hata oluştu: {str(e)}', 'danger')
    
    return render_template('user/form.html', form=form, title='Kullanıcı Düzenle', user=user)

@user_bp.route('/delete/<user_id>', methods=['DELETE'])
@login_required
@admin_required
def delete(user_id):
    """Kullanıcı silme işlemi"""
    # Kendini silmeye çalışıyorsa engelle
    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'Kendi hesabınızı silemezsiniz.'}), 400
    
    success = user_module.delete_user(user_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Kullanıcı başarıyla silindi.'}), 200
    else:
        return jsonify({'success': False, 'message': 'Kullanıcı silinirken bir hata oluştu.'}), 500

@user_bp.route('/activate/<user_id>', methods=['POST'])
@login_required
@admin_required
def activate(user_id):
    """Kullanıcıyı aktifleştirme işlemi"""
    user = user_module.activate_user(user_id)
    
    if user:
        return jsonify({'success': True, 'message': 'Kullanıcı başarıyla aktifleştirildi.'}), 200
    else:
        return jsonify({'success': False, 'message': 'Kullanıcı aktifleştirilirken bir hata oluştu.'}), 500

@user_bp.route('/deactivate/<user_id>', methods=['POST'])
@login_required
@admin_required
def deactivate(user_id):
    """Kullanıcıyı deaktif etme işlemi"""
    # Kendini deaktif etmeye çalışıyorsa engelle
    if user_id == current_user.id:
        return jsonify({'success': False, 'message': 'Kendi hesabınızı deaktif edemezsiniz.'}), 400
    
    user = user_module.deactivate_user(user_id)
    
    if user:
        return jsonify({'success': True, 'message': 'Kullanıcı başarıyla deaktif edildi.'}), 200
    else:
        return jsonify({'success': False, 'message': 'Kullanıcı deaktif edilirken bir hata oluştu.'}), 500

@user_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """Kullanıcı profil sayfası"""
    user = user_module.get_user_by_id(current_user.id)
    form = UserForm(obj=user)
    
    # Admin olmayan kullanıcılar için rol ve aktiflik alanlarını kaldır
    if not current_user.is_admin():
        del form.role
        del form.is_active
    
    if form.validate_on_submit():
        try:
            # E-posta değişikliği kontrolü
            if form.email.data != user.email:
                existing_user = user_module.get_user_by_email(form.email.data)
                if existing_user:
                    flash('Bu e-posta adresi zaten kullanılıyor.', 'danger')
                    return render_template('user/profile.html', form=form, user=user)
            
            # Kullanıcı bilgilerini güncelle
            update_data = {
                'username': form.username.data,
                'email': form.email.data
            }
            
            # Admin ise rol ve aktiflik bilgilerini de güncelle
            if current_user.is_admin():
                update_data['role'] = form.role.data
                update_data['is_active'] = form.is_active.data
            
            user_module.update_user(current_user.id, update_data)
            
            # Şifre değişikliği varsa güncelle
            if form.password.data:
                user_module.change_password(current_user.id, form.password.data)
            
            flash('Profil bilgileriniz başarıyla güncellendi.', 'success')
            return redirect(url_for('user.profile'))
            
        except Exception as e:
            flash(f'Profil güncellenirken bir hata oluştu: {str(e)}', 'danger')
    
    return render_template('user/profile.html', form=form, user=user)

@user_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Şifre değiştirme sayfası"""
    form = PasswordChangeForm()
    
    if form.validate_on_submit():
        try:
            # Şifre değiştir
            success = user_module.change_password(current_user.id, form.new_password.data)
            
            if success:
                flash('Şifreniz başarıyla değiştirildi.', 'success')
                return redirect(url_for('user.profile'))
            else:
                flash('Şifre değiştirilirken bir hata oluştu.', 'danger')
            
        except Exception as e:
            flash(f'Şifre değiştirilirken bir hata oluştu: {str(e)}', 'danger')
    
    return render_template('user/change_password.html', form=form) 