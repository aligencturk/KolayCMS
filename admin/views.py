from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from models import db, User, Page, SiteSetting, ActivityLog, ContactInfo
from utils.decorators import admin_required
from utils.helpers import get_admin_stats, log_activity
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from PIL import Image

admin = Blueprint('admin', __name__)

@admin.route('/')
@login_required
@admin_required
def index():
    stats = get_admin_stats()
    return render_template('admin/index.html', stats=stats)

@admin.route('/pages')
@login_required
@admin_required
def pages():
    pages = Page.query.all()
    return render_template('admin/pages/index.html', pages=pages)

@admin.route('/pages/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_page():
    if request.method == 'POST':
        title = request.form.get('title')
        slug = request.form.get('slug')
        content = request.form.get('content')
        meta_description = request.form.get('meta_description')
        meta_keywords = request.form.get('meta_keywords')
        status = request.form.get('status', 'published')
        template = request.form.get('template', 'default')
        parent_id = request.form.get('parent_id')
        order = request.form.get('order', 0)

        # Sayfa oluştur
        page = Page(
            title=title,
            slug=slug,
            content=content,
            meta_description=meta_description,
            meta_keywords=meta_keywords,
            status=status,
            template=template,
            parent_id=parent_id if parent_id else None,
            order=order,
            author_id=current_user.id
        )

        # Kapak görseli işleme
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                
                # Görseli kaydet
                file.save(filepath)
                
                # Thumbnail oluştur
                thumb_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'thumbnails', filename)
                create_thumbnail(filepath, thumb_path)
                
                # Media kaydı oluştur
                media = Media(
                    filename=filename,
                    original_filename=file.filename,
                    mime_type=file.content_type,
                    size=os.path.getsize(filepath),
                    path=filename,
                    uploaded_by=current_user.id
                )
                db.session.add(media)
                
                # Sayfaya görseli ekle
                page.featured_image = filename

        # İletişim sayfası ise
        if slug == 'contact':
            contact_info = ContactInfo(
                address=request.form.get('address'),
                phone=request.form.get('phone'),
                email=request.form.get('email'),
                working_hours=request.form.get('working_hours'),
                google_maps_embed=request.form.get('google_maps_embed'),
                facebook=request.form.get('facebook'),
                twitter=request.form.get('twitter'),
                instagram=request.form.get('instagram'),
                linkedin=request.form.get('linkedin')
            )
            db.session.add(contact_info)
            db.session.flush()
            page.contact_info_id = contact_info.id

        try:
            db.session.add(page)
            db.session.commit()
            
            # Aktivite kaydı
            log_activity(f'Yeni sayfa oluşturuldu: {title}')
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True})
            else:
                flash('Sayfa başarıyla oluşturuldu.', 'success')
                return redirect(url_for('admin.pages'))
                
        except Exception as e:
            db.session.rollback()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'Sayfa oluşturulurken bir hata oluştu.'})
            else:
                flash('Sayfa oluşturulurken bir hata oluştu.', 'error')
                return render_template('admin/pages/new.html')

    # GET isteği için tüm sayfaları getir (üst sayfa seçimi için)
    pages = Page.query.all()
    return render_template('admin/pages/new.html', pages=pages)

@admin.route('/pages/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_page(id):
    page = Page.query.get_or_404(id)
    
    if request.method == 'POST':
        page.title = request.form.get('title')
        page.slug = request.form.get('slug')
        page.content = request.form.get('content')
        page.meta_description = request.form.get('meta_description')
        page.meta_keywords = request.form.get('meta_keywords')
        page.is_published = True if request.form.get('is_published') else False
        page.updated_at = datetime.utcnow()
        
        if page.slug == 'contact':
            if not page.contact_info:
                page.contact_info = ContactInfo()
            
            page.contact_info.address = request.form.get('contact_info[address]')
            page.contact_info.phone = request.form.get('contact_info[phone]')
            page.contact_info.email = request.form.get('contact_info[email]')
            page.contact_info.working_hours = request.form.get('contact_info[working_hours]')
            page.contact_info.google_maps = request.form.get('contact_info[google_maps]')
            page.contact_info.facebook = request.form.get('contact_info[facebook]')
            page.contact_info.twitter = request.form.get('contact_info[twitter]')
            page.contact_info.instagram = request.form.get('contact_info[instagram]')
            page.contact_info.linkedin = request.form.get('contact_info[linkedin]')

        try:
            db.session.commit()
            log_activity(f'Sayfa düzenlendi: {page.title}')
            flash('Sayfa başarıyla güncellendi.', 'success')
            return redirect(url_for('admin.pages'))
        except Exception as e:
            db.session.rollback()
            flash('Sayfa güncellenirken bir hata oluştu.', 'error')
            return render_template('admin/pages/edit.html', page=page)

    return render_template('admin/pages/edit.html', page=page)

@admin.route('/pages/delete/<int:id>')
@login_required
@admin_required
def delete_page(id):
    page = Page.query.get_or_404(id)
    try:
        if page.contact_info:
            db.session.delete(page.contact_info)
        db.session.delete(page)
        db.session.commit()
        log_activity(f'Sayfa silindi: {page.title}')
        flash('Sayfa başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Sayfa silinirken bir hata oluştu.', 'error')
    return redirect(url_for('admin.pages'))

@admin.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    settings = SiteSetting.query.first()
    if not settings:
        settings = SiteSetting()
        db.session.add(settings)
        db.session.commit()

    if request.method == 'POST':
        settings.site_name = request.form.get('site_name')
        settings.site_description = request.form.get('site_description')
        settings.site_keywords = request.form.get('site_keywords')
        settings.footer_text = request.form.get('footer_text')
        settings.google_analytics = request.form.get('google_analytics')

        try:
            db.session.commit()
            log_activity('Site ayarları güncellendi')
            flash('Ayarlar başarıyla güncellendi.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Ayarlar güncellenirken bir hata oluştu.', 'error')

    return render_template('admin/settings.html', settings=settings)

@admin.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        user = current_user
        user.username = request.form.get('username')
        user.email = request.form.get('email')
        
        password = request.form.get('password')
        if password:
            user.password_hash = generate_password_hash(password)
        
        try:
            db.session.commit()
            log_activity('Profil güncellendi')
            flash('Profiliniz başarıyla güncellendi.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Profil güncellenirken bir hata oluştu.', 'error')
            
    return render_template('admin/profile.html')

@admin.route('/activity-logs')
@login_required
@admin_required
def activity_logs():
    logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).all()
    return render_template('admin/activity_logs.html', logs=logs)

@admin.route('/upload/image', methods=['POST'])
@login_required
@admin_required
def upload_image():
    if 'upload' not in request.files:
        return jsonify({'error': 'Dosya yüklenmedi'}), 400
        
    file = request.files['upload']
    if file.filename == '':
        return jsonify({'error': 'Dosya seçilmedi'}), 400
        
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Görseli kaydet
        file.save(filepath)
        
        # Thumbnail oluştur
        thumb_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'thumbnails', filename)
        create_thumbnail(filepath, thumb_path)
        
        # Media kaydı oluştur
        media = Media(
            filename=filename,
            original_filename=file.filename,
            mime_type=file.content_type,
            size=os.path.getsize(filepath),
            path=filename,
            uploaded_by=current_user.id
        )
        db.session.add(media)
        db.session.commit()
        
        return jsonify({
            'url': url_for('static', filename=f'uploads/{filename}'),
            'uploaded': 1
        })
        
    return jsonify({'error': 'Geçersiz dosya türü'}), 400

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_thumbnail(source_path, thumb_path):
    # Thumbnail klasörünü oluştur
    os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
    
    # Görseli aç ve thumbnail oluştur
    with Image.open(source_path) as img:
        # En-boy oranını koru
        img.thumbnail((300, 300))
        img.save(thumb_path) 