from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app.modules.themes.views import themes_bp
from app.models import Theme
from app.decorators import admin_required
from app import db
import uuid
from datetime import datetime

@themes_bp.route('/')
@login_required
@admin_required
def index():
    """Temaları listele"""
    themes_ref = db.collection('themes').stream()
    themes = [Theme(**doc.to_dict(), id=doc.id) for doc in themes_ref]
    return render_template('themes/index.html', themes=themes)

@themes_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Yeni tema oluştur"""
    if request.method == 'POST':
        # Form verilerini al
        name = request.form.get('name')
        description = request.form.get('description')
        primary_color = request.form.get('primary_color', '#00BCD4')
        secondary_color = request.form.get('secondary_color', '#f44336')
        font_family = request.form.get('font_family', 'sans-serif')
        
        # CSS değişkenlerini oluştur
        css_variables = {
            'color-bg': request.form.get('color_bg', '#ffffff'),
            'color-text': request.form.get('color_text', '#333333'),
            'color-header-bg': request.form.get('color_header_bg', '#f9f9f9'),
            'color-footer-bg': request.form.get('color_footer_bg', '#1a202c'),
            'font-size-base': request.form.get('font_size_base', '16px'),
            'border-radius': request.form.get('border_radius', '8px'),
        }
        
        # Tema örneği oluştur
        theme = Theme(
            name=name,
            description=description,
            primary_color=primary_color,
            secondary_color=secondary_color,
            font_family=font_family,
            css_variables=css_variables,
            is_active=False,
            id=str(uuid.uuid4()),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Firestore'a kaydet
        db.collection('themes').document(theme.id).set(theme.to_dict())
        
        flash('Tema başarıyla oluşturuldu', 'success')
        return redirect(url_for('themes.index'))
        
    return render_template('themes/create.html')

@themes_bp.route('/<theme_id>')
@login_required
@admin_required
def view(theme_id):
    """Tema detaylarını görüntüle"""
    theme_ref = db.collection('themes').document(theme_id).get()
    if not theme_ref.exists:
        flash('Tema bulunamadı', 'error')
        return redirect(url_for('themes.index'))
        
    theme = Theme(**theme_ref.to_dict(), id=theme_ref.id)
    return render_template('themes/view.html', theme=theme)

@themes_bp.route('/<theme_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(theme_id):
    """Tema düzenle"""
    theme_ref = db.collection('themes').document(theme_id).get()
    if not theme_ref.exists:
        flash('Tema bulunamadı', 'error')
        return redirect(url_for('themes.index'))
        
    theme_data = theme_ref.to_dict()
    
    if request.method == 'POST':
        # Form verilerini al
        name = request.form.get('name')
        description = request.form.get('description')
        primary_color = request.form.get('primary_color')
        secondary_color = request.form.get('secondary_color')
        font_family = request.form.get('font_family')
        
        # CSS değişkenlerini güncelle
        css_variables = theme_data.get('css_variables', {})
        css_variables.update({
            'color-bg': request.form.get('color_bg'),
            'color-text': request.form.get('color_text'),
            'color-header-bg': request.form.get('color_header_bg'),
            'color-footer-bg': request.form.get('color_footer_bg'),
            'font-size-base': request.form.get('font_size_base'),
            'border-radius': request.form.get('border_radius'),
        })
        
        # Veritabanını güncelle
        db.collection('themes').document(theme_id).update({
            'name': name,
            'description': description,
            'primary_color': primary_color,
            'secondary_color': secondary_color,
            'font_family': font_family,
            'css_variables': css_variables,
            'updated_at': datetime.now()
        })
        
        flash('Tema başarıyla güncellendi', 'success')
        return redirect(url_for('themes.view', theme_id=theme_id))
        
    theme = Theme(**theme_data, id=theme_id)
    return render_template('themes/edit.html', theme=theme)

@themes_bp.route('/<theme_id>/activate', methods=['POST'])
@login_required
@admin_required
def activate(theme_id):
    """Temayı aktifleştir"""
    # Önce tüm temaları devre dışı bırak
    themes_ref = db.collection('themes').stream()
    batch = db.batch()
    
    for theme_doc in themes_ref:
        theme_ref = db.collection('themes').document(theme_doc.id)
        batch.update(theme_ref, {'is_active': False})
    
    # Şimdi seçilen temayı aktifleştir
    theme_ref = db.collection('themes').document(theme_id)
    batch.update(theme_ref, {'is_active': True})
    
    # Batch işlemini uygula
    batch.commit()
    
    flash('Tema başarıyla aktifleştirildi', 'success')
    return redirect(url_for('themes.index'))

@themes_bp.route('/<theme_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(theme_id):
    """Temayı sil"""
    # Aktif tema ise silmeyi engelle
    theme_ref = db.collection('themes').document(theme_id).get()
    if theme_ref.exists and theme_ref.to_dict().get('is_active'):
        flash('Aktif tema silinemez', 'error')
        return redirect(url_for('themes.index'))
    
    # Değilse sil
    db.collection('themes').document(theme_id).delete()
    
    flash('Tema başarıyla silindi', 'success')
    return redirect(url_for('themes.index')) 