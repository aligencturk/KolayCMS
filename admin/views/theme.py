from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
from apps.models import SiteSettings
from apps.extensions import db
import os
import shutil
from werkzeug.utils import secure_filename

# Blueprint adını değiştir
theme_bp = Blueprint('theme_bp', __name__)

@theme_bp.route('/settings/theme/templates')
@login_required
def theme_templates():
    """Tema şablonları listesi sayfası"""
    settings = SiteSettings.query.first()
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
        db.session.commit()
    
    return render_template('admin/settings/theme_templates.html', active_theme=settings.active_theme)

@theme_bp.route('/settings/theme/templates/<template_type>')
@login_required
def edit_theme_template(template_type):
    """Şablon düzenleme sayfası"""
    settings = SiteSettings.query.first()
    active_theme = settings.active_theme if settings else 'default'
    template_file = get_template_file(template_type, active_theme)
    
    if not template_file:
        flash('Geçersiz şablon türü.', 'error')
        return redirect(url_for('theme_bp.theme_templates'))
    
    try:
        with open(template_file, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        flash('Şablon dosyası bulunamadı.', 'error')
        return redirect(url_for('theme_bp.theme_templates'))
    
    return render_template('admin/settings/edit_template.html',
                         template_type=template_type,
                         template_file=os.path.basename(template_file),
                         template_content=template_content,
                         active_theme=active_theme)

@theme_bp.route('/settings/theme/templates/<template_type>/save', methods=['POST'])
@login_required
def save_theme_template(template_type):
    """Şablon değişikliklerini kaydet"""
    settings = SiteSettings.query.first()
    active_theme = settings.active_theme if settings else 'default'
    
    if not request.form.get('content'):
        flash('İçerik boş olamaz.', 'error')
        return redirect(url_for('theme_bp.edit_theme_template', template_type=template_type))
    
    template_file = get_template_file(template_type, active_theme)
    if not template_file:
        flash('Geçersiz şablon türü.', 'error')
        return redirect(url_for('theme_bp.theme_templates'))
    
    # Yedek al
    backup_file = template_file + '.bak'
    try:
        shutil.copy2(template_file, backup_file)
    except Exception as e:
        flash(f'Yedek alınamadı: {str(e)}', 'error')
        return redirect(url_for('theme_bp.edit_theme_template', template_type=template_type))
    
    # Değişiklikleri kaydet
    try:
        with open(template_file, 'w', encoding='utf-8') as f:
            f.write(request.form['content'])
        flash('Değişiklikler başarıyla kaydedildi.', 'success')
    except Exception as e:
        # Hata durumunda yedeği geri yükle
        shutil.copy2(backup_file, template_file)
        flash(f'Değişiklikler kaydedilemedi: {str(e)}', 'error')
    
    # Yedeği sil
    try:
        os.remove(backup_file)
    except:
        pass
    
    return redirect(url_for('theme_bp.edit_theme_template', template_type=template_type))

@theme_bp.route('/settings/theme/templates/<template_type>/reset')
@login_required
def reset_theme_template(template_type):
    """Şablonu varsayılan haline döndür"""
    settings = SiteSettings.query.first()
    active_theme = settings.active_theme if settings else 'default'
    template_file = get_template_file(template_type, active_theme)
    default_file = template_file.replace(active_theme, 'default')
    
    if not os.path.exists(default_file):
        flash('Varsayılan şablon bulunamadı.', 'error')
        return redirect(url_for('theme_bp.edit_theme_template', template_type=template_type))
    
    try:
        shutil.copy2(default_file, template_file)
        flash('Şablon varsayılan haline döndürüldü.', 'success')
    except Exception as e:
        flash(f'Şablon sıfırlanamadı: {str(e)}', 'error')
    
    return redirect(url_for('theme_bp.edit_theme_template', template_type=template_type))

def get_template_file(template_type, active_theme):
    """Şablon dosyasının tam yolunu döndür"""
    template_files = {
        'index': f'templates/themes/{active_theme}/index.html',
        'about': f'templates/themes/{active_theme}/about.html',
        'services': f'templates/themes/{active_theme}/services.html',
        'contact': f'templates/themes/{active_theme}/contact.html',
        'blog': f'templates/themes/{active_theme}/blog.html',
        'blog_detail': f'templates/themes/{active_theme}/blog_detail.html',
        'blog_category': f'templates/themes/{active_theme}/blog_category.html',
        'blog_tag': f'templates/themes/{active_theme}/blog_tag.html',
        'header': f'templates/themes/{active_theme}/header.html',
        'footer': f'templates/themes/{active_theme}/footer.html',
        'sidebar': f'templates/themes/{active_theme}/sidebar.html',
        'css': f'static/themes/{active_theme}/css/style.css',
        'js': f'static/themes/{active_theme}/js/main.js'
    }
    return os.path.join(current_app.root_path, template_files.get(template_type, '')) 