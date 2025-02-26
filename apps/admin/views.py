from flask import render_template, request, redirect, url_for, flash, current_app, jsonify, session, g, send_file, abort
from flask_login import login_required, current_user
from apps.models import Page, db, User, Content, Product, ActivityLog, BlogPost, Slide, Service, AboutSection, VideoSection, Category, Order, SiteSettings, Project, TeamMember, Testimonial, ContactInfo, Menu, Theme, Widget, MenuItem
from . import admin_bp
from slugify import slugify
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import shutil
from apps.forms import ThemeSettingsForm
from flask_wtf.csrf import generate_csrf
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField
from wtforms.validators import DataRequired
import json
import zipfile
import tempfile
import sqlite3

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Bu sayfaya erişim için admin yetkisi gereklidir.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_admin_stats():
    """Admin paneli için istatistikleri al"""
    try:
        stats = {
            'users_count': User.query.count(),
            'pages_count': Page.query.count(),
            'blog_posts_count': BlogPost.query.count(),
            'menus_count': Menu.query.count(),
            'services_count': Service.query.count(),
            'projects_count': Project.query.count(),
            'team_count': TeamMember.query.count(),
            'testimonials_count': Testimonial.query.count(),
            'slides_count': Slide.query.count()
        }
        
        # Son aktiviteler
        recent_activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(5).all()
        stats['recent_activities'] = recent_activities
        
        # Son blog yazıları
        recent_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).limit(5).all()
        stats['recent_posts'] = recent_posts
        
        # Son kayıtlı kullanıcılar
        recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
        stats['recent_users'] = recent_users
        
        # Logları konsola yazdır
        current_app.logger.info(f"Admin istatistikleri: {stats}")
        
        return stats
    except Exception as e:
        current_app.logger.error(f"Admin istatistikleri alınırken hata: {str(e)}")
        return {
            'users_count': 0,
            'pages_count': 0,
            'blog_posts_count': 0,
            'menus_count': 0,
            'services_count': 0,
            'projects_count': 0,
            'team_count': 0,
            'testimonials_count': 0,
            'slides_count': 0,
            'recent_activities': [],
            'recent_posts': [],
            'recent_users': []
        }

def log_activity(action, status='info', details=None):
    """
    Yönetici panelindeki aktiviteleri loglar.
    
    Args:
        action (str): Yapılan işlemin açıklaması
        status (str): İşlemin durumu (success, error, info, warning)
        details (str, optional): İşlem detayları
    """
    try:
        activity = ActivityLog(
            user_id=current_user.id,
            action=action,
            status=status,
            details=details,
            timestamp=datetime.now()
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f'Aktivite logu oluşturma hatası: {str(e)}')
        db.session.rollback()

def get_db():
    if 'db' not in g:
        g.db = db
    return g.db

@admin_bp.route('/')
@login_required
@admin_required
def index():
    # İstatistikleri ve son aktiviteleri tek sorguda al
    stats = get_admin_stats()
    recent_activities = ActivityLog.query.options(
        db.joinedload(ActivityLog.user)
    ).order_by(ActivityLog.timestamp.desc()).limit(5).all()
    
    return render_template('admin/index.html', 
                         stats=stats, 
                         recent_activities=recent_activities)

@admin_bp.route('/logs')
@login_required
@admin_required
def logs():
    """Sistem loglarını görüntüle"""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    # Logları sayfalandırarak getir
    pagination = ActivityLog.query.order_by(
        ActivityLog.timestamp.desc()
    ).paginate(page=page, per_page=per_page)
    
    logs = pagination.items
    stats = get_admin_stats()
    
    return render_template('admin/logs.html',
                         logs=logs,
                         pagination=pagination,
                         stats=stats)

def init_admin(admin):
    """Admin panelini başlat"""
    pass  # Şimdilik boş bırakıyoruz

def create_default_content():
    """Varsayılan içerikleri oluşturur"""
    try:
        # Ana Sayfa
        if not Page.query.filter_by(slug='ana-sayfa').first():
            home_page = Page(
                title='Ana Sayfa',
                slug='ana-sayfa',
                content='KolayCMS\'e Hoş Geldiniz',
                is_published=True
            )
            db.session.add(home_page)
        
        # Hakkımızda Sayfası
        if not Page.query.filter_by(slug='hakkimizda').first():
            about_page = Page(
                title='Hakkımızda',
                slug='hakkimizda',
                content='Firmamız hakkında bilgiler',
                is_published=True
            )
            db.session.add(about_page)
        
        # İletişim Sayfası
        if not Page.query.filter_by(slug='iletisim').first():
            contact_page = Page(
                title='İletişim',
                slug='iletisim',
                content='İletişim bilgilerimiz',
                is_published=True
            )
            db.session.add(contact_page)
        
        # Ana Menü
        main_menu = Menu.query.filter_by(title='Ana Menü').first()
        if not main_menu:
            # Ana Menü
            main_menu = Menu(
                title='Ana Menü',
                url='#',
                menu_type='header',
                order=0
            )
            db.session.add(main_menu)
            db.session.flush()  # ID'yi almak için flush yapıyoruz
            
            # Ana Sayfa Menü Öğesi
            home_menu = Menu(
                title='Ana Sayfa',
                url='/',
                menu_type='header',
                order=0,
                parent_id=main_menu.id
            )
            db.session.add(home_menu)
            
            # Hakkımızda Menü Öğesi
            about_menu = Menu(
                title='Hakkımızda',
                url='/hakkimizda',
                menu_type='header',
                order=1,
                parent_id=main_menu.id
            )
            db.session.add(about_menu)
            
            # İletişim Menü Öğesi
            contact_menu = Menu(
                title='İletişim',
                url='/iletisim',
                menu_type='header',
                order=2,
                parent_id=main_menu.id
            )
            db.session.add(contact_menu)
        
        # İletişim Bilgileri
        if not ContactInfo.query.first():
            contact_info = ContactInfo(
                address='Örnek Adres',
                phone='+90 555 555 5555',
                email='info@kolaycms.com',
                working_hours='Pazartesi - Cuma: 09:00 - 18:00'
            )
            db.session.add(contact_info)
        
        db.session.commit()
        current_app.logger.info('Varsayılan içerikler başarıyla oluşturuldu')
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Varsayılan içerik oluşturma hatası: {str(e)}')
        raise

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def profile():
    """Admin profil sayfası"""
    if request.method == 'POST':
        try:
            # Profil güncelleme işlemleri
            current_user.username = request.form.get('username', current_user.username)
            current_user.email = request.form.get('email', current_user.email)
            
            # Şifre değişikliği kontrolü
            new_password = request.form.get('new_password')
            if new_password:
                current_user.set_password(new_password)
            
            db.session.commit()
            flash('Profil başarıyla güncellendi.', 'success')
            log_activity('Profil güncellendi', 'success')
            return redirect(url_for('admin.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('Profil güncellenirken bir hata oluştu.', 'error')
            log_activity('Profil güncelleme hatası', 'error', str(e))
            
    return render_template('admin/profile.html',
                         user=current_user,
                         stats=get_admin_stats())

@admin_bp.route('/pages')
@login_required
@admin_required
def pages_list():
    """Sayfaları listele"""
    pages = Page.query.order_by(Page.created_at.desc()).all()
    header_menus = Menu.query.filter_by(menu_type='header', parent_id=None).order_by(Menu.order).all()
    footer_menus = Menu.query.filter_by(menu_type='footer', parent_id=None).order_by(Menu.order).all()
    stats = get_admin_stats()
    return render_template('admin/pages/list.html',
                         pages=pages,
                         header_menus=header_menus,
                         footer_menus=footer_menus,
                         stats=stats)

@admin_bp.route('/pages/create', methods=['GET', 'POST'])
@login_required
@admin_required
def page_create():
    """Yeni sayfa oluştur"""
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            content = request.form.get('content')
            slug = request.form.get('slug') or slugify(title)
            is_published = bool(request.form.get('is_published'))
            
            page = Page(
                title=title,
                content=content,
                slug=slug,
                is_published=is_published,
                created_by=current_user.id
            )
            
            db.session.add(page)
            db.session.commit()
            
            flash('Sayfa başarıyla oluşturuldu.', 'success')
            log_activity('Yeni sayfa oluşturuldu', 'success', f'Sayfa: {title}')
            return redirect(url_for('admin.pages_list'))
            
        except Exception as e:
            db.session.rollback()
            flash('Sayfa oluşturulurken bir hata oluştu.', 'error')
            log_activity('Sayfa oluşturma hatası', 'error', str(e))
    
    return render_template('admin/pages/create.html',
                         stats=get_admin_stats())

@admin_bp.route('/pages/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def page_edit(id):
    """Sayfa düzenle"""
    page = Page.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            page.title = request.form.get('title')
            page.content = request.form.get('content')
            page.slug = request.form.get('slug') or slugify(page.title)
            page.is_published = bool(request.form.get('is_published'))
            page.updated_at = datetime.now()
            
            db.session.commit()
            
            flash('Sayfa başarıyla güncellendi.', 'success')
            log_activity('Sayfa güncellendi', 'success', f'Sayfa: {page.title}')
            return redirect(url_for('admin.pages_list'))
            
        except Exception as e:
            db.session.rollback()
            flash('Sayfa güncellenirken bir hata oluştu.', 'error')
            log_activity('Sayfa güncelleme hatası', 'error', str(e))
    
    return render_template('admin/pages/edit.html',
                         page=page,
                         stats=get_admin_stats())

@admin_bp.route('/pages/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def page_delete(id):
    """Sayfa sil"""
    page = Page.query.get_or_404(id)
    
    try:
        title = page.title
        db.session.delete(page)
        db.session.commit()
        
        flash('Sayfa başarıyla silindi.', 'success')
        log_activity('Sayfa silindi', 'success', f'Sayfa: {title}')
        
    except Exception as e:
        db.session.rollback()
        flash('Sayfa silinirken bir hata oluştu.', 'error')
        log_activity('Sayfa silme hatası', 'error', str(e))
    
    return redirect(url_for('admin.pages_list'))

@admin_bp.route('/pages/bulk-action', methods=['POST'])
@login_required
@admin_required
def pages_bulk_action():
    """Sayfalar için toplu işlem yap"""
    action = request.form.get('action')
    page_ids = request.form.get('page_ids', '')
    
    if not page_ids:
        flash('İşlem yapılacak sayfa seçilmedi.', 'warning')
        return redirect(url_for('admin.pages_list'))
    
    try:
        ids = [int(id) for id in page_ids.split(',')]
        pages = Page.query.filter(Page.id.in_(ids)).all()
        
        count = len(pages)
        if action == 'publish':
            for page in pages:
                page.is_published = True
            
            db.session.commit()
            flash(f'{count} sayfa başarıyla yayınlandı.', 'success')
            log_activity(f'{count} sayfa toplu yayınlandı', 'success')
            
        elif action == 'draft':
            for page in pages:
                page.is_published = False
            
            db.session.commit()
            flash(f'{count} sayfa taslak olarak işaretlendi.', 'success')
            log_activity(f'{count} sayfa toplu olarak taslak yapıldı', 'success')
            
        elif action == 'delete':
            titles = [page.title for page in pages]
            for page in pages:
                db.session.delete(page)
            
            db.session.commit()
            flash(f'{count} sayfa başarıyla silindi.', 'success')
            log_activity(f'{count} sayfa toplu silindi', 'success', f'Sayfalar: {", ".join(titles)}')
        
    except Exception as e:
        db.session.rollback()
        flash('Toplu işlem sırasında bir hata oluştu.', 'error')
        log_activity('Toplu işlem hatası', 'error', str(e))
    
    return redirect(url_for('admin.pages_list'))

@admin_bp.route('/menus')
@login_required
@admin_required
def menus():
    """Menüleri listele"""
    header_menus = Menu.query.filter_by(menu_type='header', parent_id=None).order_by(Menu.order).all()
    footer_menus = Menu.query.filter_by(menu_type='footer', parent_id=None).order_by(Menu.order).all()
    
    stats = get_admin_stats()
    return render_template('admin/menus/list.html',
                         header_menus=header_menus,
                         footer_menus=footer_menus,
                         stats=stats)

@admin_bp.route('/menus/create', methods=['GET', 'POST'])
@login_required
@admin_required
def menu_create():
    """Yeni menü oluştur"""
    parent_menus = Menu.query.filter_by(parent_id=None).all()
    pages = Page.query.filter_by(is_published=True).order_by(Page.title).all()
    
    if request.method == 'POST':
        try:
            title = request.form.get('title')
            url = request.form.get('url')
            menu_type = request.form.get('menu_type')
            parent_id = request.form.get('parent_id')
            order = request.form.get('order', 0, type=int)
            
            # Sayfa seçildiyse URL'yi güncelle
            page_id = request.form.get('page_id')
            if page_id:
                page = Page.query.get(page_id)
                if page:
                    url = f'/page/{page.slug}'
            
            if parent_id == "0":
                parent_id = None
            
            menu = Menu(
                title=title,
                url=url,
                menu_type=menu_type,
                parent_id=parent_id,
                order=order
            )
            
            db.session.add(menu)
            db.session.commit()
            
            flash('Menü başarıyla oluşturuldu.', 'success')
            log_activity('Yeni menü oluşturuldu', 'success', f'Menü: {title}')
            return redirect(url_for('admin.menus'))
            
        except Exception as e:
            db.session.rollback()
            flash('Menü oluşturulurken bir hata oluştu.', 'error')
            log_activity('Menü oluşturma hatası', 'error', str(e))
    
    return render_template('admin/menus/create.html',
                         parent_menus=parent_menus,
                         pages=pages,
                         stats=get_admin_stats())

@admin_bp.route('/menus/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def menu_edit(id):
    """Menü düzenle"""
    menu = Menu.query.get_or_404(id)
    parent_menus = Menu.query.filter(Menu.id != id).filter_by(parent_id=None).all()
    pages = Page.query.filter_by(is_published=True).order_by(Page.title).all()
    
    if request.method == 'POST':
        try:
            menu.title = request.form.get('title')
            menu.url = request.form.get('url')
            menu.menu_type = request.form.get('menu_type')
            
            # Sayfa seçildiyse URL'yi güncelle
            page_id = request.form.get('page_id')
            if page_id:
                page = Page.query.get(page_id)
                if page:
                    menu.url = f'/page/{page.slug}'
            
            parent_id = request.form.get('parent_id')
            if parent_id == "0":
                menu.parent_id = None
            else:
                # Kendisinin altında olan bir menüyü parent olarak seçmesini engelle
                if int(parent_id) != id and not is_child_menu(int(parent_id), id):
                    menu.parent_id = parent_id
            
            menu.order = request.form.get('order', 0, type=int)
            
            db.session.commit()
            
            flash('Menü başarıyla güncellendi.', 'success')
            log_activity('Menü güncellendi', 'success', f'Menü: {menu.title}')
            return redirect(url_for('admin.menus'))
            
        except Exception as e:
            db.session.rollback()
            flash('Menü güncellenirken bir hata oluştu.', 'error')
            log_activity('Menü güncelleme hatası', 'error', str(e))
    
    return render_template('admin/menus/edit.html',
                         menu=menu,
                         parent_menus=parent_menus,
                         pages=pages,
                         stats=get_admin_stats())

@admin_bp.route('/menus/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def menu_delete(id):
    """Menü sil"""
    menu = Menu.query.get_or_404(id)
    
    try:
        # Alt menüleri de silme işlemi
        title = menu.title
        delete_menu_recursively(menu)
        
        flash('Menü başarıyla silindi.', 'success')
        log_activity('Menü silindi', 'success', f'Menü: {title}')
        
    except Exception as e:
        db.session.rollback()
        flash('Menü silinirken bir hata oluştu.', 'error')
        log_activity('Menü silme hatası', 'error', str(e))
    
    return redirect(url_for('admin.menus'))

def delete_menu_recursively(menu):
    """Menüyü ve alt menüleri recursive olarak sil"""
    children = Menu.query.filter_by(parent_id=menu.id).all()
    
    for child in children:
        delete_menu_recursively(child)
    
    db.session.delete(menu)
    db.session.commit()

def is_child_menu(parent_id, menu_id):
    """Bir menünün, belirtilen menünün alt menüsü olup olmadığını kontrol eder"""
    children = Menu.query.filter_by(parent_id=menu_id).all()
    
    for child in children:
        if child.id == parent_id or is_child_menu(parent_id, child.id):
            return True
    
    return False

@admin_bp.route('/menus/reorder', methods=['POST'])
@login_required
@admin_required
def menu_reorder():
    """Menü sıralama düzeni güncelleme"""
    try:
        menu_order = request.json
        
        for item in menu_order:
            menu = Menu.query.get(item['id'])
            if menu:
                menu.parent_id = item['parent_id'] if item['parent_id'] != 0 else None
                menu.order = item['order']
        
        db.session.commit()
        log_activity('Menü sıralaması güncellendi', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        log_activity('Menü sıralama hatası', 'error', str(e))
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/contents')
@login_required
@admin_required
def contents_list():
    """İçerik yönetimi sayfası"""
    try:
        # Sayfalar - web sitesindeki sayfaları da göster
        pages = Page.query.order_by(Page.title).all()
        
        # Blog yazıları
        blog_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
        
        # Menüler
        menus = Menu.query.order_by(Menu.menu_type, Menu.order).all()
        
        # Hakkımızda bölümü
        about_sections = AboutSection.query.all()
        
        # Hizmetler
        services = Service.query.order_by(Service.order).all()
        
        # Projeler
        projects = Project.query.order_by(Project.order).all()
        
        # Ekip üyeleri
        team_members = TeamMember.query.order_by(TeamMember.order).all()
        
        # Müşteri yorumları
        testimonials = Testimonial.query.order_by(Testimonial.order).all()
        
        # İletişim bilgileri
        contact_info = ContactInfo.query.first()
        
        # Slider
        slides = Slide.query.order_by(Slide.order).all()
        
        # İstatistikleri al
        stats = get_admin_stats()
        
        # Aktiviteyi logla
        log_activity("İçerik yönetimi sayfası görüntülendi")
        
        return render_template('admin/contents/list.html',
                             pages=pages,
                             blog_posts=blog_posts,
                             menus=menus,
                             about_sections=about_sections,
                             services=services,
                             projects=projects,
                             team_members=team_members,
                             testimonials=testimonials,
                             contact_info=contact_info,
                             slides=slides,
                             stats=stats)
    except Exception as e:
        current_app.logger.error(f"İçerik listesi gösterilirken hata: {str(e)}")
        flash(f"İçerik listesi yüklenirken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.index'))

# Hakkımızda bölümü için route'lar
@admin_bp.route('/contents/about')
@login_required
@admin_required
def about_info():
    """Hakkımızda bölümünü göster"""
    try:
        about = AboutSection.query.first()
        stats = get_admin_stats()
        return render_template('admin/contents/about/edit.html', 
                              about=about,
                              stats=stats)
    except Exception as e:
        current_app.logger.error(f"Hakkımızda bölümü gösterilirken hata: {str(e)}")
        flash(f"Hakkımızda bölümü yüklenirken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.contents_list'))

@admin_bp.route('/contents/about/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def about_edit():
    """Hakkımızda bölümünü düzenle"""
    try:
        about = AboutSection.query.first()
        if not about:
            about = AboutSection()
            db.session.add(about)
        
        if request.method == 'POST':
            about.title = request.form.get('title')
            about.subtitle = request.form.get('subtitle')
            about.content = request.form.get('content')
            about.stats_title = request.form.get('stats_title')
            about.stats_content = request.form.get('stats_content')
            about.is_active = 'is_active' in request.form
            
            # İstatistik öğelerini işle
            stats_items = []
            stats_numbers = request.form.getlist('stats_number[]')
            stats_texts = request.form.getlist('stats_text[]')
            for number, text in zip(stats_numbers, stats_texts):
                if number and text:
                    stats_items.append({"number": number, "text": text})
            about.stats_items = stats_items
            
            # Görsel yükleme işlemleri
            if 'image' in request.files and request.files['image'].filename:
                image = request.files['image']
                if image and allowed_file(image.filename):
                    # Eski görseli sil (eğer varsa)
                    if about.image_path and os.path.exists(os.path.join(current_app.static_folder, about.image_path)):
                        os.remove(os.path.join(current_app.static_folder, about.image_path))
                    
                    # Güvenli dosya adı oluştur
                    from werkzeug.utils import secure_filename
                    import os
                    filename = secure_filename(image.filename)
                    # Dosya yolunu oluştur
                    image_path = os.path.join('uploads', 'about', filename)
                    # Dizin yoksa oluştur
                    os.makedirs(os.path.join(current_app.static_folder, 'uploads', 'about'), exist_ok=True)
                    # Dosyayı kaydet
                    image.save(os.path.join(current_app.static_folder, image_path))
                    # Veri tabanında güncelle
                    about.image_path = image_path
            
            # Veri tabanında güncelle
            about.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Aktiviteyi logla
            log_activity("Hakkımızda bölümü güncellendi")
            
            flash('Hakkımızda bölümü başarıyla güncellendi!', 'success')
            return redirect(url_for('admin.about_info'))
            
        return render_template('admin/contents/about/edit.html', about=about)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Hakkımızda bölümü düzenlenirken hata: {str(e)}")
        flash(f"Hakkımızda bölümü düzenlenirken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.contents_list'))

# Hizmetler için route'lar
@admin_bp.route('/contents/services')
@login_required
@admin_required
def services_list():
    """Hizmetleri listele"""
    try:
        # Servisleri sıraya göre getir
        services = Service.query.order_by(Service.order).all()
        # Admin istatistiklerini al
        stats = get_admin_stats()
        # İçerik türlerine göre sayıları al
        services_count = Service.query.count()
        projects_count = Project.query.count()
        team_count = TeamMember.query.count()
        testimonials_count = Testimonial.query.count()
        slides_count = Slide.query.count()
        
        # Ana içerik sayfasını göster, burada tüm içerik kartları var
        return render_template('admin/contents/list.html', 
                              services=services,
                              stats=stats,
                              services_count=services_count,
                              projects_count=projects_count,
                              team_count=team_count,
                              testimonials_count=testimonials_count,
                              slides_count=slides_count)
    except Exception as e:
        current_app.logger.error(f"Hizmetler listelenirken hata: {str(e)}")
        flash(f"Hizmetler listelenirken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.index'))

# Blog yazıları için route'lar
@admin_bp.route('/contents/blog')
@login_required
@admin_required
def blog_list():
    """Blog yazılarını listele"""
    try:
        blog_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
        stats = get_admin_stats()
        return render_template('admin/contents/blog/list.html', 
                              blog_posts=blog_posts,
                              stats=stats)
    except Exception as e:
        current_app.logger.error(f"Blog yazıları listelenirken hata: {str(e)}")
        flash(f"Blog yazıları listelenirken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.contents_list'))

@admin_bp.route('/contents/blog/create', methods=['GET', 'POST'])
@login_required
@admin_required
def blog_create():
    """Yeni blog yazısı oluştur"""
    try:
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            excerpt = request.form.get('excerpt')
            slug = request.form.get('slug') or slugify(title)
            is_published = 'is_published' in request.form
            image_path = None
            
            # Görsel yükleme işlemleri
            if 'image' in request.files and request.files['image'].filename:
                image = request.files['image']
                if image and allowed_file(image.filename):
                    # Güvenli dosya adı oluştur
                    from werkzeug.utils import secure_filename
                    import os
                    filename = secure_filename(image.filename)
                    # Dosya yolunu oluştur
                    image_path = os.path.join('uploads', 'blog', filename)
                    # Dizin yoksa oluştur
                    os.makedirs(os.path.join(current_app.static_folder, 'uploads', 'blog'), exist_ok=True)
                    # Dosyayı kaydet
                    image.save(os.path.join(current_app.static_folder, image_path))
            
            # Yeni blog yazısı oluştur
            new_post = BlogPost(
                title=title,
                content=content,
                excerpt=excerpt,
                slug=slug,
                image_path=image_path,
                is_published=is_published,
                author_id=current_user.id
            )
            db.session.add(new_post)
            db.session.commit()
            
            # Aktiviteyi logla
            log_activity(f"Yeni blog yazısı oluşturuldu: {title}")
            
            flash('Blog yazısı başarıyla oluşturuldu!', 'success')
            return redirect(url_for('admin.blog_list'))
            
        return render_template('admin/contents/blog/create.html')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Blog yazısı oluşturulurken hata: {str(e)}")
        flash(f"Blog yazısı oluşturulurken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.blog_list'))

@admin_bp.route('/contents/blog/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def blog_edit(id):
    """Blog yazısı düzenle"""
    try:
        post = BlogPost.query.get_or_404(id)
        
        if request.method == 'POST':
            post.title = request.form.get('title')
            post.content = request.form.get('content')
            post.excerpt = request.form.get('excerpt')
            post.slug = request.form.get('slug') or slugify(post.title)
            post.is_published = 'is_published' in request.form
            
            # Görsel yükleme işlemleri
            if 'image' in request.files and request.files['image'].filename:
                image = request.files['image']
                if image and allowed_file(image.filename):
                    # Eski görseli sil (eğer varsa)
                    if post.image_path and os.path.exists(os.path.join(current_app.static_folder, post.image_path)):
                        os.remove(os.path.join(current_app.static_folder, post.image_path))
                    
                    # Güvenli dosya adı oluştur
                    from werkzeug.utils import secure_filename
                    import os
                    filename = secure_filename(image.filename)
                    # Dosya yolunu oluştur
                    image_path = os.path.join('uploads', 'blog', filename)
                    # Dizin yoksa oluştur
                    os.makedirs(os.path.join(current_app.static_folder, 'uploads', 'blog'), exist_ok=True)
                    # Dosyayı kaydet
                    image.save(os.path.join(current_app.static_folder, image_path))
                    # Veri tabanında güncelle
                    post.image_path = image_path
            
            # Veri tabanında güncelle
            post.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Aktiviteyi logla
            log_activity(f"Blog yazısı düzenlendi: {post.title}")
            
            flash('Blog yazısı başarıyla güncellendi!', 'success')
            return redirect(url_for('admin.blog_list'))
            
        return render_template('admin/contents/blog/edit.html', post=post)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Blog yazısı düzenlenirken hata: {str(e)}")
        flash(f"Blog yazısı düzenlenirken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.blog_list'))

@admin_bp.route('/contents/blog/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def blog_delete(id):
    """Blog yazısı sil"""
    try:
        post = BlogPost.query.get_or_404(id)
        
        # Blog görseli varsa silme işlemi
        if post.image_path and os.path.exists(os.path.join(current_app.static_folder, post.image_path)):
            os.remove(os.path.join(current_app.static_folder, post.image_path))
        
        # Blog başlığını geçici olarak sakla
        post_title = post.title
        
        # Veritabanından sil
        db.session.delete(post)
        db.session.commit()
        
        # Aktiviteyi logla
        log_activity(f"Blog yazısı silindi: {post_title}")
        
        flash('Blog yazısı başarıyla silindi!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Blog yazısı silinirken hata: {str(e)}")
        flash(f"Blog yazısı silinirken bir hata oluştu: {str(e)}", "danger")
    
    return redirect(url_for('admin.blog_list'))

# Sayfalar için route'lar
@admin_bp.route('/contents/pages')
@login_required
@admin_required
def content_pages_list():
    """Sayfaları listele"""
    try:
        pages = Page.query.order_by(Page.title).all()
        stats = get_admin_stats()
        return render_template('admin/contents/pages/list.html', 
                              pages=pages,
                              stats=stats)
    except Exception as e:
        current_app.logger.error(f"Sayfalar listelenirken hata: {str(e)}")
        flash(f"Sayfalar listelenirken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.contents_list'))

@admin_bp.route('/contents/pages/create', methods=['GET', 'POST'])
@login_required
@admin_required
def pages_create():
    """Yeni sayfa oluştur"""
    try:
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            slug = request.form.get('slug') or slugify(title)
            is_published = 'is_published' in request.form
            
            # Yeni sayfa oluştur
            new_page = Page(
                title=title,
                content=content,
                slug=slug,
                is_published=is_published,
                author_id=current_user.id
            )
            db.session.add(new_page)
            db.session.commit()
            
            # Aktiviteyi logla
            log_activity(f"Yeni sayfa oluşturuldu: {title}")
            
            flash('Sayfa başarıyla oluşturuldu!', 'success')
            return redirect(url_for('admin.pages_list'))
            
        return render_template('admin/contents/pages/create.html')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Sayfa oluşturulurken hata: {str(e)}")
        flash(f"Sayfa oluşturulurken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.pages_list'))

@admin_bp.route('/contents/pages/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def pages_edit(id):
    """Sayfa düzenle"""
    try:
        page = Page.query.get_or_404(id)
        
        if request.method == 'POST':
            page.title = request.form.get('title')
            page.content = request.form.get('content')
            page.slug = request.form.get('slug') or slugify(page.title)
            page.is_published = 'is_published' in request.form
            
            # Veri tabanında güncelle
            page.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Aktiviteyi logla
            log_activity(f"Sayfa düzenlendi: {page.title}")
            
            flash('Sayfa başarıyla güncellendi!', 'success')
            return redirect(url_for('admin.pages_list'))
            
        return render_template('admin/contents/pages/edit.html', page=page)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Sayfa düzenlenirken hata: {str(e)}")
        flash(f"Sayfa düzenlenirken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.pages_list'))

@admin_bp.route('/contents/pages/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def pages_delete(id):
    """Sayfa sil"""
    try:
        page = Page.query.get_or_404(id)
        
        # Sayfa başlığını geçici olarak sakla
        page_title = page.title
        
        # Veritabanından sil
        db.session.delete(page)
        db.session.commit()
        
        # Aktiviteyi logla
        log_activity(f"Sayfa silindi: {page_title}")
        
        flash('Sayfa başarıyla silindi!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Sayfa silinirken hata: {str(e)}")
        flash(f"Sayfa silinirken bir hata oluştu: {str(e)}", "danger")
    
    return redirect(url_for('admin.pages_list'))

# Menüler için route'lar
@admin_bp.route('/contents/menus')
@login_required
@admin_required
def menus_list():
    """Menüleri listele"""
    try:
        menus = Menu.query.order_by(Menu.menu_type, Menu.order).all()
        stats = get_admin_stats()
        return render_template('admin/contents/menus/list.html', 
                              menus=menus,
                              stats=stats)
    except Exception as e:
        current_app.logger.error(f"Menüler listelenirken hata: {str(e)}")
        flash(f"Menüler listelenirken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.contents_list'))

@admin_bp.route('/contents/menus/create', methods=['GET', 'POST'])
@login_required
@admin_required
def menus_create():
    """Yeni menü oluştur"""
    try:
        if request.method == 'POST':
            title = request.form.get('title')
            url = request.form.get('url')
            menu_type = request.form.get('menu_type')
            parent_id = request.form.get('parent_id')
            order = request.form.get('order', 0, type=int)
            is_active = 'is_active' in request.form
            
            # Sayfa seçildiyse URL'yi güncelle
            page_id = request.form.get('page_id')
            if page_id:
                page = Page.query.get(page_id)
                if page:
                    url = f'/page/{page.slug}'
            
            if parent_id == "0":
                parent_id = None
            
            # Yeni menü oluştur
            new_menu = Menu(
                title=title,
                url=url,
                menu_type=menu_type,
                parent_id=parent_id,
                order=order,
                is_active=is_active
            )
            db.session.add(new_menu)
            db.session.commit()
            
            # Aktiviteyi logla
            log_activity(f"Yeni menü oluşturuldu: {title}")
            
            flash('Menü başarıyla oluşturuldu!', 'success')
            return redirect(url_for('admin.menus_list'))
            
        # Form için gerekli veriler
        parent_menus = Menu.query.filter_by(parent_id=None).all()
        pages = Page.query.filter_by(is_published=True).order_by(Page.title).all()
        return render_template('admin/contents/menus/create.html',
                             parent_menus=parent_menus,
                             pages=pages)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Menü oluşturulurken hata: {str(e)}")
        flash(f"Menü oluşturulurken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.menus_list'))

@admin_bp.route('/contents/menus/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def menus_edit(id):
    """Menü düzenle"""
    try:
        menu = Menu.query.get_or_404(id)
        
        if request.method == 'POST':
            menu.title = request.form.get('title')
            menu.url = request.form.get('url')
            menu.menu_type = request.form.get('menu_type')
            menu.parent_id = request.form.get('parent_id')
            menu.order = request.form.get('order', 0, type=int)
            menu.is_active = 'is_active' in request.form
            
            # Sayfa seçildiyse URL'yi güncelle
            page_id = request.form.get('page_id')
            if page_id:
                page = Page.query.get(page_id)
                if page:
                    menu.url = f'/page/{page.slug}'
            
            if menu.parent_id == "0":
                menu.parent_id = None
            
            # Veri tabanında güncelle
            menu.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Aktiviteyi logla
            log_activity(f"Menü düzenlendi: {menu.title}")
            
            flash('Menü başarıyla güncellendi!', 'success')
            return redirect(url_for('admin.menus_list'))
            
        # Form için gerekli veriler
        parent_menus = Menu.query.filter(Menu.id != id, Menu.parent_id == None).all()
        pages = Page.query.filter_by(is_published=True).order_by(Page.title).all()
        return render_template('admin/contents/menus/edit.html',
                             menu=menu,
                             parent_menus=parent_menus,
                             pages=pages)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Menü düzenlenirken hata: {str(e)}")
        flash(f"Menü düzenlenirken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.menus_list'))

@admin_bp.route('/contents/menus/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def menus_delete(id):
    """Menü sil"""
    try:
        menu = Menu.query.get_or_404(id)
        
        # Alt menüleri de sil
        sub_menus = Menu.query.filter_by(parent_id=id).all()
        for sub_menu in sub_menus:
            db.session.delete(sub_menu)
        
        # Menü başlığını geçici olarak sakla
        menu_title = menu.title
        
        # Veritabanından sil
        db.session.delete(menu)
        db.session.commit()
        
        # Aktiviteyi logla
        log_activity(f"Menü silindi: {menu_title}")
        
        flash('Menü başarıyla silindi!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Menü silinirken hata: {str(e)}")
        flash(f"Menü silinirken bir hata oluştu: {str(e)}", "danger")
    
    return redirect(url_for('admin.menus_list'))

@admin_bp.route('/contents/menus/reorder', methods=['POST'])
@login_required
@admin_required
def menus_reorder():
    """Menü sıralamasını güncelle"""
    try:
        menu_orders = request.get_json()
        for menu_id, order in menu_orders.items():
            menu = Menu.query.get(menu_id)
            if menu:
                menu.order = order
        
        db.session.commit()
        
        # Aktiviteyi logla
        log_activity("Menü sıralaması güncellendi")
        
        return jsonify({"status": "success"})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Menü sıralaması güncellenirken hata: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

# İçerik sıralama için genel route
@admin_bp.route('/contents/<string:content_type>/reorder', methods=['POST'])
@login_required
@admin_required
def content_reorder(content_type):
    """İçerik sıralamasını güncelle"""
    try:
        content_orders = request.get_json()
        
        # İçerik türüne göre model seç
        model_map = {
            'services': Service,
            'projects': Project,
            'team': TeamMember,
            'testimonials': Testimonial,
            'slides': Slide,
            'videos': VideoSection
        }
        
        model = model_map.get(content_type)
        if not model:
            return jsonify({"status": "error", "message": "Geçersiz içerik türü"}), 400
        
        # Sıralamayı güncelle
        for content_id, order in content_orders.items():
            content = model.query.get(content_id)
            if content:
                content.order = order
        
        db.session.commit()
        
        # Aktiviteyi logla
        log_activity(f"{content_type.capitalize()} sıralaması güncellendi")
        
        return jsonify({"status": "success"})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"İçerik sıralaması güncellenirken hata: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@admin_bp.route('/users')
@login_required
@admin_required
def users_list():
    """Kullanıcıları listele"""
    try:
        users = User.query.order_by(User.created_at.desc()).all()
        stats = get_admin_stats()
        return render_template('admin/users/list.html', 
                            users=users,
                            stats=stats)
    except Exception as e:
        current_app.logger.error(f"Kullanıcılar listelenirken hata: {str(e)}")
        flash(f"Kullanıcılar listelenirken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.index'))

@admin_bp.route('/users/create', methods=['POST'])
@login_required
@admin_required
def user_create():
    """Yeni kullanıcı oluştur"""
    try:
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        
        # Kullanıcı adı ve email kontrolü
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor.', 'error')
            return redirect(url_for('admin.users_list'))
            
        if User.query.filter_by(email=email).first():
            flash('Bu e-posta adresi zaten kullanılıyor.', 'error')
            return redirect(url_for('admin.users_list'))
        
        # Yeni kullanıcı oluştur
        user = User(
            username=username,
            email=email,
            role=role,
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Kullanıcı başarıyla oluşturuldu.', 'success')
        log_activity(f'Yeni kullanıcı oluşturuldu: {username}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Kullanıcı oluşturulurken bir hata oluştu: {str(e)}', 'error')
        log_activity('Kullanıcı oluşturma hatası', 'error', str(e))
        
    return redirect(url_for('admin.users_list'))

@admin_bp.route('/users/<int:id>/edit', methods=['POST'])
@login_required
@admin_required
def user_edit(id):
    """Kullanıcı düzenle"""
    try:
        user = User.query.get_or_404(id)
        
        # Mevcut kullanıcı kendisini admin rolünden çıkaramaz
        if current_user.id == user.id and user.role == 'admin' and request.form.get('role') != 'admin':
            flash('Kendi admin rolünüzü değiştiremezsiniz.', 'error')
            return redirect(url_for('admin.users_list'))
        
        # Kullanıcı adı değişikliği kontrolü
        new_username = request.form.get('username')
        if new_username != user.username and User.query.filter_by(username=new_username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor.', 'error')
            return redirect(url_for('admin.users_list'))
        
        # Email değişikliği kontrolü
        new_email = request.form.get('email')
        if new_email != user.email and User.query.filter_by(email=new_email).first():
            flash('Bu e-posta adresi zaten kullanılıyor.', 'error')
            return redirect(url_for('admin.users_list'))
        
        # Kullanıcı bilgilerini güncelle
        user.username = new_username
        user.email = new_email
        user.role = request.form.get('role', user.role)
        
        # Şifre değişikliği varsa uygula
        new_password = request.form.get('password')
        if new_password:
            user.set_password(new_password)
        
        db.session.commit()
        flash('Kullanıcı başarıyla güncellendi.', 'success')
        log_activity(f'Kullanıcı güncellendi: {user.username}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Kullanıcı güncellenirken bir hata oluştu: {str(e)}', 'error')
        log_activity('Kullanıcı güncelleme hatası', 'error', str(e))
        
    return redirect(url_for('admin.users_list'))

@admin_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def user_delete(id):
    """Kullanıcı sil"""
    try:
        user = User.query.get_or_404(id)
        
        # Kullanıcı kendisini silmeye çalışıyorsa engelle
        if current_user.id == user.id:
            flash('Kendinizi silemezsiniz.', 'error')
            return redirect(url_for('admin.users_list'))
        
        username = user.username
        db.session.delete(user)
        db.session.commit()
        
        flash('Kullanıcı başarıyla silindi.', 'success')
        log_activity(f'Kullanıcı silindi: {username}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Kullanıcı silinirken bir hata oluştu: {str(e)}', 'error')
        log_activity('Kullanıcı silme hatası', 'error', str(e))
        
    return redirect(url_for('admin.users_list'))

@admin_bp.route('/template-editor')
@login_required
@admin_required
def template_editor():
    """Şablon düzenleyici sayfası"""
    try:
        # Aktif temayı al
        settings = SiteSettings.query.first()
        active_theme = settings.active_theme if settings else None
        
        # Tüm temaları al
        themes = Theme.query.all()
        
        return render_template('admin/theme/template_editor.html',
                            active_theme=active_theme,
                            themes=themes,
                            stats=get_admin_stats())
    except Exception as e:
        current_app.logger.error(f"Şablon düzenleyici gösterilirken hata: {str(e)}")
        flash(f"Şablon düzenleyici yüklenirken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.index'))

@admin_bp.route('/template-editor/save', methods=['POST'])
@login_required
@admin_required
def save_template():
    """Şablon değişikliklerini kaydet"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Veri bulunamadı'}), 400
            
        content = data.get('content')
        section = data.get('section')
        content_type = data.get('type')
        
        if not all([content, section, content_type]):
            return jsonify({'error': 'Eksik parametreler'}), 400
            
        # Aktif temayı al
        settings = SiteSettings.query.first()
        if not settings or not settings.active_theme:
            return jsonify({'error': 'Aktif tema bulunamadı'}), 404
            
        theme = Theme.query.get(settings.active_theme)
        if not theme:
            return jsonify({'error': 'Tema bulunamadı'}), 404
            
        # Tema içeriğini güncelle
        if content_type == 'html':
            theme.template = json.dumps(content)
        elif content_type == 'css':
            theme.css = json.dumps(content)
        elif content_type == 'js':
            theme.js = json.dumps(content)
            
        db.session.commit()
        
        # Aktiviteyi logla
        log_activity(f"Tema şablonu güncellendi: {section} - {content_type}")
        
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Şablon kaydedilirken hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/template-editor/preview')
@login_required
@admin_required
def preview_template():
    """Şablon önizleme sayfası"""
    try:
        # Aktif temayı al
        settings = SiteSettings.query.first()
        if not settings or not settings.active_theme:
            flash('Aktif tema bulunamadı.', 'error')
            return redirect(url_for('admin.template_editor'))
            
        theme = Theme.query.get(settings.active_theme)
        if not theme:
            flash('Tema bulunamadı.', 'error')
            return redirect(url_for('admin.template_editor'))
            
        # Tema içeriğini yükle
        template_content = json.loads(theme.template) if theme.template else {}
        css_content = json.loads(theme.css) if theme.css else {}
        js_content = json.loads(theme.js) if theme.js else {}
        
        return render_template('admin/theme/preview.html',
                            template=template_content,
                            css=css_content,
                            js=js_content)
                            
    except Exception as e:
        current_app.logger.error(f"Şablon önizleme gösterilirken hata: {str(e)}")
        flash(f"Şablon önizleme yüklenirken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.template_editor'))

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    """Site ayarları sayfası"""
    try:
        settings = SiteSettings.query.first()
        if not settings:
            settings = SiteSettings(
                site_title='KolayCMS',
                site_description='Modern ve Kolay Yönetilebilir İçerik Yönetim Sistemi',
                theme_version='1.0',
                theme_name='default',
                is_customized=False
            )
            db.session.add(settings)
            db.session.commit()
            
        if request.method == 'POST':
            # Genel ayarlar
            settings.site_title = request.form.get('site_title')
            settings.site_description = request.form.get('site_description')
            settings.meta_keywords = request.form.get('meta_keywords')
            settings.meta_description = request.form.get('meta_description')
            settings.google_analytics = request.form.get('google_analytics')
            settings.facebook_pixel = request.form.get('facebook_pixel')
            settings.custom_css = request.form.get('custom_css')
            settings.custom_js = request.form.get('custom_js')
            
            # Logo yükleme
            if 'logo' in request.files and request.files['logo'].filename:
                logo = request.files['logo']
                if logo and allowed_file(logo.filename):
                    # Eski logoyu sil
                    if settings.logo_path and os.path.exists(os.path.join(current_app.static_folder, settings.logo_path)):
                        os.remove(os.path.join(current_app.static_folder, settings.logo_path))
                    
                    # Yeni logoyu kaydet
                    filename = secure_filename(logo.filename)
                    logo_path = os.path.join('uploads', 'logos', filename)
                    os.makedirs(os.path.join(current_app.static_folder, 'uploads', 'logos'), exist_ok=True)
                    logo.save(os.path.join(current_app.static_folder, logo_path))
                    settings.logo_path = logo_path
            
            # Favicon yükleme
            if 'favicon' in request.files and request.files['favicon'].filename:
                favicon = request.files['favicon']
                if favicon and allowed_file(favicon.filename):
                    # Eski favicon'u sil
                    if settings.favicon_path and os.path.exists(os.path.join(current_app.static_folder, settings.favicon_path)):
                        os.remove(os.path.join(current_app.static_folder, settings.favicon_path))
                    
                    # Yeni favicon'u kaydet
                    filename = secure_filename(favicon.filename)
                    favicon_path = os.path.join('uploads', 'favicon', filename)
                    os.makedirs(os.path.join(current_app.static_folder, 'uploads', 'favicon'), exist_ok=True)
                    favicon.save(os.path.join(current_app.static_folder, favicon_path))
                    settings.favicon_path = favicon_path
            
            # İletişim bilgileri
            settings.contact_email = request.form.get('contact_email')
            settings.contact_phone = request.form.get('contact_phone')
            settings.contact_address = request.form.get('contact_address')
            settings.contact_map = request.form.get('contact_map')
            
            # Sosyal medya
            settings.facebook_url = request.form.get('facebook_url')
            settings.twitter_url = request.form.get('twitter_url')
            settings.instagram_url = request.form.get('instagram_url')
            settings.linkedin_url = request.form.get('linkedin_url')
            settings.youtube_url = request.form.get('youtube_url')
            
            # SMTP ayarları
            settings.smtp_host = request.form.get('smtp_host')
            settings.smtp_port = request.form.get('smtp_port')
            settings.smtp_user = request.form.get('smtp_user')
            settings.smtp_pass = request.form.get('smtp_pass')
            settings.smtp_from_name = request.form.get('smtp_from_name')
            settings.smtp_from_email = request.form.get('smtp_from_email')
            
            db.session.commit()
            flash('Ayarlar başarıyla güncellendi.', 'success')
            log_activity('Site ayarları güncellendi', 'success')
            return redirect(url_for('admin.settings'))
            
        return render_template('admin/settings.html',
                             settings=settings,
                             stats=get_admin_stats())
                             
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Site ayarları gösterilirken hata: {str(e)}")
        flash(f"Site ayarları yüklenirken bir hata oluştu: {str(e)}", "danger")
        return redirect(url_for('admin.index'))
