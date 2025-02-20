from flask import render_template, request, redirect, url_for, flash, current_app, jsonify, session
from flask_login import login_required, current_user
from apps.models import Page, db, User, Content, Product, ActivityLog, BlogPost, Slide, Service, AboutSection, VideoSection, Category, Order, SiteSettings, Project, TeamMember, Testimonial, ContactInfo, Menu
from . import admin_bp
from slugify import slugify
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import shutil
from apps.forms import ThemeSettingsForm

def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Bu sayfaya erişim için admin yetkisi gereklidir.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def get_admin_stats():
    """Admin paneli için istatistikleri döndürür"""
    stats = {
        'total_users': 0,
        'total_pages': 0,
        'total_menus': 0,
        'low_stock': 0,
    }
    return stats

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

@admin_bp.route('/')
@login_required
@admin_required
def index():
    stats = get_admin_stats()
    recent_activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(5).all()
    
    return render_template('admin/index.html', 
                         stats=stats, 
                         recent_activities=recent_activities)

@admin_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@admin_required
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        # Kullanıcı adı ve email kontrolü
        if username != current_user.username:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Bu kullanıcı adı zaten kullanılıyor.', 'error')
                return redirect(url_for('admin.profile'))
                
        if email != current_user.email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('Bu e-posta adresi zaten kullanılıyor.', 'error')
                return redirect(url_for('admin.profile'))
        
        # Şifre değişikliği kontrolü
        if current_password and new_password:
            if not current_user.check_password(current_password):
                flash('Mevcut şifreniz yanlış.', 'error')
                return redirect(url_for('admin.profile'))
            current_user.set_password(new_password)
        
        # Bilgileri güncelle
        current_user.username = username
        current_user.email = email
        
        try:
            db.session.commit()
            flash('Profil bilgileriniz başarıyla güncellendi.', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Profil güncelleme hatası: {str(e)}')
            flash('Profil güncellenirken bir hata oluştu.', 'error')
            
        return redirect(url_for('admin.profile'))
        
    return render_template('admin/profile.html')

@admin_bp.route('/pages')
@login_required
@admin_required
def pages_list():
    # Varsayılan sayfaları kontrol et ve ekle
    default_pages = [
        {
            'title': 'Ana Sayfa',
            'slug': '',
            'content': 'Ana sayfa içeriği',
            'is_published': True
        },
        {
            'title': 'Hakkımızda',
            'slug': 'about',
            'content': 'Hakkımızda sayfası içeriği',
            'is_published': True
        },
        {
            'title': 'Hizmetler',
            'slug': 'services',
            'content': 'Hizmetler sayfası içeriği',
            'is_published': True
        },
        {
            'title': 'Blog',
            'slug': 'blog',
            'content': 'Blog sayfası içeriği',
            'is_published': True
        },
        {
            'title': 'İletişim',
            'slug': 'contact',
            'content': 'İletişim sayfası içeriği',
            'is_published': True
        }
    ]
    
    # Her varsayılan sayfa için kontrol et ve yoksa ekle
    for page_data in default_pages:
        page = Page.query.filter_by(slug=page_data['slug']).first()
        if not page:
            page = Page(**page_data)
            db.session.add(page)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Varsayılan sayfa ekleme hatası: {str(e)}')

    # Tüm sayfaları getir
    pages = Page.query.order_by(Page.created_at.desc()).all()
    stats = get_admin_stats()
    return render_template('admin/pages/list.html', pages=pages, stats=stats, now=datetime.now())

@admin_bp.route('/pages/create', methods=['GET', 'POST'])
@login_required
@admin_required
def pages_create():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        slug = request.form.get('slug') or slugify(title)
        is_published = bool(request.form.get('is_published'))
        
        page = Page(
            title=title,
            content=content,
            slug=slug,
            is_published=is_published,
            created_at=datetime.now()
        )
        
        db.session.add(page)
        db.session.commit()
        
        flash('Sayfa başarıyla oluşturuldu.', 'success')
        return redirect(url_for('admin.pages_list'))
        
    stats = get_admin_stats()
    return render_template('admin/pages/create.html', stats=stats)

@admin_bp.route('/pages/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def pages_edit(id):
    page = Page.query.get_or_404(id)
    stats = get_admin_stats()

    if request.method == 'POST':
        try:
            # Form verilerini al
            page.title = request.form.get('title')
            page.slug = request.form.get('slug')
            page.content = request.form.get('content')
            page.meta_description = request.form.get('meta_description')
            page.meta_keywords = request.form.get('meta_keywords')
            page.is_published = True if request.form.get('is_published') else False
            page.updated_at = datetime.now()

            if page.slug == 'contact':
                if not page.contact_info:
                    contact_info = ContactInfo(
                        address=request.form.get('address', ''),
                        phone=request.form.get('phone', ''),
                        email=request.form.get('email', ''),
                        google_maps_embed=request.form.get('google_maps_embed', ''),
                        working_hours=request.form.get('working_hours', ''),
                        facebook=request.form.get('facebook', ''),
                        twitter=request.form.get('twitter', ''),
                        instagram=request.form.get('instagram', ''),
                        linkedin=request.form.get('linkedin', '')
                    )
                    db.session.add(contact_info)
                    db.session.flush()  # ID'yi almak için flush
                    page.contact_info_id = contact_info.id
                else:
                    page.contact_info.address = request.form.get('address', '')
                    page.contact_info.phone = request.form.get('phone', '')
                    page.contact_info.email = request.form.get('email', '')
                    page.contact_info.google_maps_embed = request.form.get('google_maps_embed', '')
                    page.contact_info.working_hours = request.form.get('working_hours', '')
                    page.contact_info.facebook = request.form.get('facebook', '')
                    page.contact_info.twitter = request.form.get('twitter', '')
                    page.contact_info.instagram = request.form.get('instagram', '')
                    page.contact_info.linkedin = request.form.get('linkedin', '')

            # Değişiklikleri kaydet
            db.session.commit()
            
            # Önbelleği temizle
            db.session.expire_all()
            
            flash('Sayfa başarıyla güncellendi!', 'success')
            return redirect(url_for('admin.pages_list'))
            
        except Exception as e:
            current_app.logger.error(f'Sayfa güncelleme hatası: {str(e)}')
            db.session.rollback()
            flash('Sayfa güncellenirken bir hata oluştu!', 'error')
            return render_template('admin/pages/edit.html', page=page, stats=stats)

    return render_template('admin/pages/edit.html', page=page, stats=stats)

@admin_bp.route('/pages/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def pages_delete(id):
    try:
        page = Page.query.get_or_404(id)
        
        # Varsayılan sayfaları silmeyi engelle
        if page.slug in ['', 'about', 'contact', 'blog', 'services']:
            return jsonify({
                'success': False,
                'message': 'Varsayılan sayfalar silinemez.'
            }), 400
        
        # Sayfanın iletişim bilgilerini sil
        if page.contact_info:
            db.session.delete(page.contact_info)
            
        db.session.delete(page)
        db.session.commit()
        
        # Aktivite logu oluştur
        activity = ActivityLog(
            user_id=current_user.id,
            action=f'Sayfa silindi: {page.title}',
            details=f'Sayfa ID: {page.id}'
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sayfa başarıyla silindi.'
        })
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Sayfa silme hatası: {str(e)}')
        return jsonify({
            'success': False,
            'message': 'Sayfa silinirken bir hata oluştu.'
        }), 500

@admin_bp.route('/pages/preview/<int:id>')
@login_required
@admin_required
def pages_preview(id):
    page = Page.query.get_or_404(id)
    stats = get_admin_stats()
    return render_template('admin/pages/preview.html', page=page, stats=stats)

@admin_bp.route('/users')
@login_required
@admin_required
def users_list():
    users = User.query.order_by(User.created_at.desc()).all()
    stats = get_admin_stats()
    return render_template('admin/users/list.html', users=users, stats=stats)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def users_create():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'user')
        is_active = bool(request.form.get('is_active'))
        
        # Kullanıcı adı ve email kontrolü
        if User.query.filter_by(username=username).first():
            flash('Bu kullanıcı adı zaten kullanılıyor.', 'error')
            return redirect(url_for('admin.users_create'))
            
        if User.query.filter_by(email=email).first():
            flash('Bu e-posta adresi zaten kullanılıyor.', 'error')
            return redirect(url_for('admin.users_create'))
        
        user = User(
            username=username,
            email=email,
            role=role,
            is_active=is_active,
            created_at=datetime.now()
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            flash('Kullanıcı başarıyla oluşturuldu.', 'success')
            return redirect(url_for('admin.users_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Kullanıcı oluşturma hatası: {str(e)}')
            flash('Kullanıcı oluşturulurken bir hata oluştu.', 'error')
            
    stats = get_admin_stats()
    return render_template('admin/users/create.html', stats=stats)

@admin_bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def users_edit(id):
    user = User.query.get_or_404(id)
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        new_password = request.form.get('new_password')
        role = request.form.get('role')
        is_active = bool(request.form.get('is_active'))
        
        # Kullanıcı adı kontrolü
        if username != user.username:
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Bu kullanıcı adı zaten kullanılıyor.', 'error')
                return redirect(url_for('admin.users_edit', id=id))
        
        # Email kontrolü
        if email != user.email:
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                flash('Bu e-posta adresi zaten kullanılıyor.', 'error')
                return redirect(url_for('admin.users_edit', id=id))
        
        # Bilgileri güncelle
        user.username = username
        user.email = email
        user.role = role
        user.is_active = is_active
        
        # Şifre değişikliği
        if new_password:
            user.set_password(new_password)
        
        try:
            db.session.commit()
            flash('Kullanıcı başarıyla güncellendi.', 'success')
            return redirect(url_for('admin.users_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Kullanıcı güncelleme hatası: {str(e)}')
            flash('Kullanıcı güncellenirken bir hata oluştu.', 'error')
            
    stats = get_admin_stats()
    return render_template('admin/users/edit.html', user=user, stats=stats)

@admin_bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def users_delete(id):
    if current_user.id == id:
        flash('Kendi hesabınızı silemezsiniz.', 'error')
        return redirect(url_for('admin.users_list'))
        
    user = User.query.get_or_404(id)
    
    try:
        db.session.delete(user)
        db.session.commit()
        flash('Kullanıcı başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kullanıcı silme hatası: {str(e)}')
        flash('Kullanıcı silinirken bir hata oluştu.', 'error')
        
    return redirect(url_for('admin.users_list'))

@admin_bp.route('/contents')
@login_required
@admin_required
def contents_list():
    # Eğer hiç slayt yoksa, varsayılan slaytları ekle
    if Slide.query.count() == 0:
        default_slides = [
            {
                'title': 'Business Agency Profit Your Marketing',
                'description': 'It is a long established fact that a reader will be distracted by the readable content of a page when',
                'button_text': 'Contact Us',
                'button_url': '/contact',
                'order': 1,
                'is_active': True,
                'image_path': '/static/cobsin_template/images/banner-bg.png'
            },
            {
                'title': 'Grow Your Business With Us',
                'description': 'We help businesses achieve their goals through innovative solutions and strategic planning',
                'button_text': 'Read More',
                'button_url': '/about',
                'order': 2,
                'is_active': True,
                'image_path': '/static/cobsin_template/images/banner-bg.png'
            }
        ]
        
        # Template'den resimleri kopyala
        import shutil
        import os
        
        template_path = os.path.join(current_app.root_path, 'static', 'cobsin_template', 'images', 'banner-bg.png')
        upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'slides')
        os.makedirs(upload_path, exist_ok=True)
        
        for i, slide_data in enumerate(default_slides, 1):
            # Resmi kopyala
            new_filename = f'default-slide-{i}.png'
            new_path = os.path.join(upload_path, new_filename)
            try:
                shutil.copy2(template_path, new_path)
                slide_data['image_path'] = f'/static/uploads/slides/{new_filename}'
            except Exception as e:
                current_app.logger.error(f'Resim kopyalama hatası: {str(e)}')
                slide_data['image_path'] = '/static/cobsin_template/images/banner-bg.png'
            
            slide = Slide(**slide_data)
            db.session.add(slide)
        
        try:
            db.session.commit()
            flash('Örnek slaytlar başarıyla eklendi.', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Slayt ekleme hatası: {str(e)}')
            flash('Slaytlar eklenirken bir hata oluştu.', 'error')
    
    # Eğer hakkımızda bölümü yoksa, varsayılan içeriği ekle
    about = AboutSection.query.first()
    if not about:
        about = AboutSection(
            title="About Us",
            subtitle="It is a long established fact that a reader will be distracted by the readable content of a page when",
            content="There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words",
            stats_title="Our Statistics",
            stats_content="Our achievements in numbers",
            stats_items=[
                {"number": "100+", "text": "Happy Clients"},
                {"number": "150+", "text": "Projects Completed"},
                {"number": "10+", "text": "Years Experience"},
                {"number": "24/7", "text": "Support"}
            ],
            is_active=True
        )
        db.session.add(about)
        db.session.commit()
    
    # Eğer hiç hizmet yoksa, varsayılan hizmetleri ekle
    if Service.query.count() == 0:
        default_services = [
            {
                'title': 'Selection of Business',
                'description': 'There are many variations of passages of Lorem Ipsum available, but the form, by injected humour, or randomised',
                'icon': 'fas fa-briefcase',
                'order': 1,
                'is_active': True
            },
            {
                'title': 'Research and Analytics',
                'description': 'There are many variations of passages of Lorem Ipsum available, but the form, by injected humour, or randomised',
                'icon': 'fas fa-chart-line',
                'order': 2,
                'is_active': True
            },
            {
                'title': 'Business Plans',
                'description': 'There are many variations of passages of Lorem Ipsum available, but the form, by injected humour, or randomised',
                'icon': 'fas fa-file-alt',
                'order': 3,
                'is_active': True
            }
        ]
        
        for service_data in default_services:
            service = Service(**service_data)
            db.session.add(service)
        
        db.session.commit()
    
    # Eğer hiç blog yazısı yoksa, varsayılan blog yazısını ekle
    if BlogPost.query.count() == 0:
        blog = BlogPost(
            title="Easily Grow Your Business Earn More Money",
            content="There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words There uffered alteration in some form, by injected humour, or randomised words",
            excerpt="Learn how to grow your business and earn more money with our expert tips and strategies.",
            slug="grow-your-business",
            is_published=True,
            author_id=current_user.id,
            created_at=datetime.now()
        )
        try:
            db.session.add(blog)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Blog ekleme hatası: {str(e)}')
    
    # Eğer video bölümü yoksa, varsayılan video içeriğini ekle
    video = VideoSection.query.first()
    if not video:
        video = VideoSection(
            title="Follow Our Video For Solved Your Problem",
            url="https://www.youtube.com/watch?v=example",
            is_active=True
        )
        db.session.add(video)
        db.session.commit()

    # Mevcut içerikleri getir
    blog_posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    slides = Slide.query.order_by(Slide.order.asc()).all()
    about_sections = AboutSection.query.all()
    services = Service.query.order_by(Service.order.asc()).all()
    projects = Project.query.order_by(Project.order.asc()).all()
    team_members = TeamMember.query.order_by(TeamMember.order.asc()).all()
    testimonials = Testimonial.query.order_by(Testimonial.order.asc()).all()
    contact_info = ContactInfo.query.first()
    video_section = VideoSection.query.first()
    
    stats = get_admin_stats()
    return render_template('admin/contents/list.html', 
                         blog_posts=blog_posts,
                         slides=slides,
                         about_sections=about_sections,
                         services=services,
                         projects=projects,
                         team_members=team_members,
                         testimonials=testimonials,
                         contact_info=contact_info,
                         video_section=video_section,
                         stats=stats)

@admin_bp.route('/contents/blog/create', methods=['GET', 'POST'])
@login_required
@admin_required
def blog_create():
    stats = get_admin_stats()
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        slug = request.form.get('slug')
        is_published = bool(request.form.get('is_published'))
        meta_title = request.form.get('meta_title')
        meta_description = request.form.get('meta_description')
        
        # Dosya yükleme işlemi
        featured_image = None
        if 'featured_image' in request.files:
            file = request.files['featured_image']
            if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'blog', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                featured_image = f'/static/uploads/blog/{filename}'
        
        blog = BlogPost(
            title=title,
            content=content,
            excerpt=excerpt,
            featured_image=featured_image,
            slug=slug,
            is_published=is_published,
            meta_title=meta_title,
            meta_description=meta_description,
            author_id=current_user.id,
            created_at=datetime.now(),
            published_at=datetime.now() if is_published else None
        )
        
        try:
            db.session.add(blog)
            db.session.commit()
            flash('Blog yazısı başarıyla oluşturuldu.', 'success')
            return redirect(url_for('admin.contents_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Blog oluşturma hatası: {str(e)}')
            flash('Blog yazısı oluşturulurken bir hata oluştu.', 'error')
            
    return render_template('admin/contents/blog/create.html', stats=stats)

@admin_bp.route('/contents/blog/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def blog_edit(id):
    stats = get_admin_stats()
    post = BlogPost.query.get_or_404(id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        excerpt = request.form.get('excerpt')
        is_published = bool(request.form.get('is_published'))
        
        try:
            post.title = title
            post.content = content
            post.excerpt = excerpt
            post.is_published = is_published
            post.published_at = datetime.now() if is_published else None
            post.updated_at = datetime.now()
            db.session.commit()
            
            flash('Blog yazısı başarıyla güncellendi.', 'success')
            return redirect(url_for('admin.contents_list'))
        except Exception as e:
            current_app.logger.error(f'Blog yazısı güncelleme hatası: {str(e)}')
            flash('Blog yazısı güncellenirken bir hata oluştu.', 'error')
            db.session.rollback()
            
    return render_template('admin/contents/blog/edit.html', post=post, stats=stats)

@admin_bp.route('/contents/blog/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def blog_delete(id):
    try:
        blog_post = BlogPost.query.get_or_404(id)
        db.session.delete(blog_post)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Blog yazısı başarıyla silindi.'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Blog silme hatası: {str(e)}')
        return jsonify({'success': False, 'message': 'Blog yazısı silinirken bir hata oluştu.'}), 500

@admin_bp.route('/contents/slide/create', methods=['GET', 'POST'])
@login_required
@admin_required
def slide_create():
    stats = get_admin_stats()
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        button_text = request.form.get('button_text')
        button_url = request.form.get('button_url')
        order = request.form.get('order')
        is_active = bool(request.form.get('is_active'))
        
        slide = Slide(
            title=title,
            description=description,
            button_text=button_text,
            button_url=button_url,
            order=order,
            is_active=is_active
        )
        
        try:
            slide.save()
            flash('Slayt başarıyla oluşturuldu.', 'success')
            return redirect(url_for('admin.contents_list'))
        except Exception as e:
            current_app.logger.error(f'Slayt oluşturma hatası: {str(e)}')
            flash('Slayt oluşturulurken bir hata oluştu.', 'error')
            
    return render_template('admin/contents/slide/create.html', stats=stats)

@admin_bp.route('/contents/slide/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def slide_edit(id):
    stats = get_admin_stats()
    slide = Slide.query.get_or_404(id)
    
    if request.method == 'POST':
        slide.title = request.form.get('title')
        slide.description = request.form.get('description')
        slide.button1_text = request.form.get('button1_text')
        slide.button1_url = request.form.get('button1_url')
        slide.button2_text = request.form.get('button2_text')
        slide.button2_url = request.form.get('button2_url')
        slide.order = request.form.get('order', type=int, default=0)
        slide.is_active = bool(request.form.get('is_active'))
        
        # Görsel yükleme işlemi
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename:
                filename = secure_filename(file.filename)
                # Benzersiz dosya adı oluştur
                unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file_path = os.path.join('uploads', 'slides', unique_filename)
                
                # Uploads/slides klasörünü oluştur
                os.makedirs(os.path.join(current_app.static_folder, 'uploads', 'slides'), exist_ok=True)
                
                # Eski görseli sil
                if slide.image:
                    old_image_path = os.path.join(current_app.static_folder, slide.image)
                    if os.path.exists(old_image_path):
                        os.remove(old_image_path)
                
                # Yeni görseli kaydet
                file.save(os.path.join(current_app.static_folder, file_path))
                slide.image = file_path
        
        try:
            db.session.commit()
            flash('Slayt başarıyla güncellendi.', 'success')
            return redirect(url_for('admin.contents_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Slayt güncelleme hatası: {str(e)}')
            flash('Slayt güncellenirken bir hata oluştu.', 'error')
    
    return render_template('admin/contents/slide/edit.html', slide=slide, stats=stats)

@admin_bp.route('/contents/slide/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def slide_delete(id):
    stats = get_admin_stats()
    slide = Slide.query.get_or_404(id)
    
    try:
        slide.delete()
        flash('Slayt başarıyla silindi.', 'success')
    except Exception as e:
        current_app.logger.error(f'Slayt silme hatası: {str(e)}')
        flash('Slayt silinirken bir hata oluştu.', 'error')
    
    return redirect(url_for('admin.contents_list'))

@admin_bp.route('/products')
@login_required
@admin_required
def products_list():
    products = Product.query.order_by(Product.created_at.desc()).all()
    categories = Category.query.order_by(Category.name.asc()).all()
    stats = get_admin_stats()
    return render_template('admin/products/list.html', 
                         products=products,
                         categories=categories,
                         stats=stats)

@admin_bp.route('/products/create', methods=['GET', 'POST'])
@login_required
@admin_required
def products_create():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = float(request.form.get('price', 0))
        stock = int(request.form.get('stock', 0))
        category_id = request.form.get('category_id')
        is_active = bool(request.form.get('is_active'))
        is_featured = bool(request.form.get('is_featured'))
        sku = request.form.get('sku')
        weight = float(request.form.get('weight', 0))
        dimensions = request.form.get('dimensions')
        meta_title = request.form.get('meta_title')
        meta_description = request.form.get('meta_description')
        
        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
            is_active=is_active,
            is_featured=is_featured,
            sku=sku,
            weight=weight,
            dimensions=dimensions,
            meta_title=meta_title,
            meta_description=meta_description
        )
        
        try:
            product.save()
            flash('Ürün başarıyla oluşturuldu.', 'success')
            return redirect(url_for('admin.products_list'))
        except Exception as e:
            current_app.logger.error(f'Ürün oluşturma hatası: {str(e)}')
            flash('Ürün oluşturulurken bir hata oluştu.', 'error')
            
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template('admin/products/create.html', categories=categories)

@admin_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def products_edit(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        product.name = request.form.get('name')
        product.description = request.form.get('description')
        product.price = float(request.form.get('price', 0))
        product.stock = int(request.form.get('stock', 0))
        product.category_id = request.form.get('category_id')
        product.is_active = bool(request.form.get('is_active'))
        product.is_featured = bool(request.form.get('is_featured'))
        product.sku = request.form.get('sku')
        product.weight = float(request.form.get('weight', 0))
        product.dimensions = request.form.get('dimensions')
        product.meta_title = request.form.get('meta_title')
        product.meta_description = request.form.get('meta_description')
        
        try:
            product.save()
            flash('Ürün başarıyla güncellendi.', 'success')
            return redirect(url_for('admin.products_list'))
        except Exception as e:
            current_app.logger.error(f'Ürün güncelleme hatası: {str(e)}')
            flash('Ürün güncellenirken bir hata oluştu.', 'error')
            
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template('admin/products/edit.html', 
                         product=product,
                         categories=categories)

@admin_bp.route('/products/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def products_delete(id):
    product = Product.query.get_or_404(id)
    
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Ürün başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Ürün silme hatası: {str(e)}')
        flash('Ürün silinirken bir hata oluştu.', 'error')
        
    return redirect(url_for('admin.products_list'))

@admin_bp.route('/categories')
@login_required
@admin_required
def categories_list():
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template('admin/categories/list.html', categories=categories)

@admin_bp.route('/categories/create', methods=['GET', 'POST'])
@login_required
@admin_required
def categories_create():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        parent_id = request.form.get('parent_id')
        
        category = Category(
            name=name,
            description=description,
            parent_id=parent_id if parent_id else None
        )
        
        try:
            category.save()
            flash('Kategori başarıyla oluşturuldu.', 'success')
            return redirect(url_for('admin.categories_list'))
        except Exception as e:
            current_app.logger.error(f'Kategori oluşturma hatası: {str(e)}')
            flash('Kategori oluşturulurken bir hata oluştu.', 'error')
            
    categories = Category.query.order_by(Category.name.asc()).all()
    return render_template('admin/categories/create.html', categories=categories)

@admin_bp.route('/categories/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def categories_edit(id):
    category = Category.query.get_or_404(id)
    
    if request.method == 'POST':
        category.name = request.form.get('name')
        category.description = request.form.get('description')
        parent_id = request.form.get('parent_id')
        category.parent_id = parent_id if parent_id else None
        
        try:
            category.save()
            flash('Kategori başarıyla güncellendi.', 'success')
            return redirect(url_for('admin.categories_list'))
        except Exception as e:
            current_app.logger.error(f'Kategori güncelleme hatası: {str(e)}')
            flash('Kategori güncellenirken bir hata oluştu.', 'error')
            
    categories = Category.query.filter(Category.id != id).order_by(Category.name.asc()).all()
    return render_template('admin/categories/edit.html', 
                         category=category,
                         categories=categories)

@admin_bp.route('/categories/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def categories_delete(id):
    category = Category.query.get_or_404(id)
    
    # Kategoriye ait ürünleri kontrol et
    if category.products.count() > 0:
        flash('Bu kategoriye ait ürünler var. Önce ürünleri başka bir kategoriye taşıyın.', 'error')
        return redirect(url_for('admin.categories_list'))
    
    try:
        db.session.delete(category)
        db.session.commit()
        flash('Kategori başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Kategori silme hatası: {str(e)}')
        flash('Kategori silinirken bir hata oluştu.', 'error')
        
    return redirect(url_for('admin.categories_list'))

@admin_bp.route('/orders')
@login_required
@admin_required
def orders_list():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    stats = get_admin_stats()
    return render_template('admin/orders/list.html', orders=orders, stats=stats)

@admin_bp.route('/orders/view/<int:id>')
@login_required
@admin_required
def orders_view(id):
    order = Order.query.get_or_404(id)
    return render_template('admin/orders/view.html', order=order)

@admin_bp.route('/orders/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def orders_edit(id):
    order = Order.query.get_or_404(id)
    
    if request.method == 'POST':
        order.status = request.form.get('status')
        order.payment_status = request.form.get('payment_status')
        order.shipping_method = request.form.get('shipping_method')
        order.tracking_number = request.form.get('tracking_number')
        order.notes = request.form.get('notes')
        
        try:
            db.session.commit()
            
            # Aktivite logu oluştur
            activity = ActivityLog(
                user_id=current_user.id,
                action=f'Sipariş #{order.id} güncellendi',
                details=f'Durum: {order.status}, Ödeme Durumu: {order.payment_status}'
            )
            db.session.add(activity)
            db.session.commit()
            
            flash('Sipariş başarıyla güncellendi.', 'success')
            return redirect(url_for('admin.orders_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Sipariş güncelleme hatası: {str(e)}')
            flash('Sipariş güncellenirken bir hata oluştu.', 'error')
            
    return render_template('admin/orders/edit.html', order=order)

@admin_bp.route('/orders/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def orders_delete(id):
    order = Order.query.get_or_404(id)
    
    try:
        # Aktivite logu oluştur
        activity = ActivityLog(
            user_id=current_user.id,
            action=f'Sipariş #{order.id} silindi',
            details=f'Toplam: {order.total} TL, Müşteri: {order.user.username}'
        )
        
        db.session.delete(order)
        db.session.add(activity)
        db.session.commit()
        
        flash('Sipariş başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Sipariş silme hatası: {str(e)}')
        flash('Sipariş silinirken bir hata oluştu.', 'error')
        
    return redirect(url_for('admin.orders_list'))

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
@admin_required
def settings():
    settings = SiteSettings.query.first()
    stats = get_admin_stats()
    
    if request.method == 'POST':
        # Temel Ayarlar
        settings.site_title = request.form.get('site_title')
        settings.site_description = request.form.get('site_description')
        settings.meta_keywords = request.form.get('meta_keywords')
        
        # Tema Ayarları
        settings.navbar_bg_color = request.form.get('navbar_bg_color', '#ffffff')
        settings.navbar_text_color = request.form.get('navbar_text_color', '#000000')
        settings.navbar_active_color = request.form.get('navbar_active_color', '#007bff')
        settings.navbar_hover_color = request.form.get('navbar_hover_color', '#0056b3')
        settings.navbar_is_fixed = bool(request.form.get('navbar_is_fixed'))
        settings.navbar_is_transparent = bool(request.form.get('navbar_is_transparent'))
        
        settings.body_bg_color = request.form.get('body_bg_color', '#ffffff')
        settings.body_text_color = request.form.get('body_text_color', '#212529')
        settings.body_link_color = request.form.get('body_link_color', '#007bff')
        settings.body_font_family = request.form.get('body_font_family', 'Poppins')
        settings.body_font_size = request.form.get('body_font_size', '14px')
        
        settings.footer_bg_color = request.form.get('footer_bg_color', '#343a40')
        settings.footer_text_color = request.form.get('footer_text_color', '#ffffff')
        settings.footer_link_color = request.form.get('footer_link_color', '#ffffff')
        
        # İletişim Bilgileri
        settings.footer_about = request.form.get('footer_about')
        settings.address = request.form.get('address')
        settings.phone = request.form.get('phone')
        settings.email = request.form.get('email')
        
        # Sosyal Medya
        settings.facebook_url = request.form.get('facebook_url')
        settings.twitter_url = request.form.get('twitter_url')
        settings.instagram_url = request.form.get('instagram_url')
        
        # Özel CSS ve JS
        settings.custom_css = request.form.get('custom_css')
        settings.custom_js = request.form.get('custom_js')
        
        # Logo ve Favicon
        logo = request.files.get('logo')
        favicon = request.files.get('favicon')
        
        if logo and allowed_file(logo.filename):
            filename = secure_filename(logo.filename)
            logo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'logos', filename)
            os.makedirs(os.path.dirname(logo_path), exist_ok=True)
            logo.save(logo_path)
            settings.logo_path = f'/static/uploads/logos/{filename}'
            
        if favicon and allowed_file(favicon.filename):
            filename = secure_filename(favicon.filename)
            favicon_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'favicons', filename)
            os.makedirs(os.path.dirname(favicon_path), exist_ok=True)
            favicon.save(favicon_path)
            settings.favicon_path = f'/static/uploads/favicons/{filename}'
        
        try:
            db.session.commit()
            
            # Aktivite logu oluştur
            activity = ActivityLog(
                user_id=current_user.id,
                action='Site ayarları güncellendi',
                details='Genel site ayarları ve tema ayarları güncellendi'
            )
            db.session.add(activity)
            db.session.commit()
            
            flash('Site ayarları başarıyla güncellendi.', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Ayar güncelleme hatası: {str(e)}')
            flash('Ayarlar güncellenirken bir hata oluştu.', 'error')
            
    return render_template('admin/settings.html', settings=settings, stats=stats)

@admin_bp.route('/settings/backup', methods=['POST'])
@login_required
@admin_required
def settings_backup():
    try:
        # Veritabanı yedeği al
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(current_app.root_path, 'backups')
        if not os.path.exists(backup_path):
            os.makedirs(backup_path)
            
        backup_file = os.path.join(backup_path, f'backup_{timestamp}.sql')
        
        # SQLite veritabanını yedekle
        with open(backup_file, 'w') as f:
            for line in current_app.db.engine.raw_connection().iterdump():
                f.write('%s\n' % line)
        
        # Aktivite logu oluştur
        activity = ActivityLog(
            user_id=current_user.id,
            action='Veritabanı yedeği alındı',
            details=f'Yedek dosyası: backup_{timestamp}.sql'
        )
        db.session.add(activity)
        db.session.commit()
        
        flash('Veritabanı yedeği başarıyla alındı.', 'success')
    except Exception as e:
        current_app.logger.error(f'Yedekleme hatası: {str(e)}')
        flash('Yedekleme işlemi sırasında bir hata oluştu.', 'error')
        
    return redirect(url_for('admin.settings'))

@admin_bp.route('/settings/restore/<filename>', methods=['POST'])
@login_required
@admin_required
def settings_restore(filename):
    try:
        backup_file = os.path.join(current_app.config['BACKUP_FOLDER'], filename)
        if not os.path.exists(backup_file):
            flash('Yedek dosyası bulunamadı.', 'error')
            return redirect(url_for('admin.settings'))

        with open(backup_file, 'r') as f:
            current_app.db.engine.raw_connection().executescript(f.read())
        
        # Aktivite logu oluştur
        activity = ActivityLog(
            user_id=current_user.id,
            action='Veritabanı geri yüklendi',
            details=f'Yedek dosyası: {filename}'
        )
        db.session.add(activity)
        db.session.commit()
        
        flash('Veritabanı yedeği başarıyla geri yüklendi.', 'success')
    except Exception as e:
        current_app.logger.error(f'Geri yükleme hatası: {str(e)}')
        flash('Geri yükleme işlemi sırasında bir hata oluştu.', 'error')
    
    return redirect(url_for('admin.settings'))

@admin_bp.route('/settings/maintenance', methods=['POST'])
@login_required
@admin_required
def settings_maintenance():
    try:
        # Geçici dosyaları temizle
        cache_path = os.path.join(current_app.root_path, 'static', 'cache')
        if os.path.exists(cache_path):
            shutil.rmtree(cache_path)
            os.makedirs(cache_path)
        
        # Eski log dosyalarını temizle
        log_path = os.path.join(current_app.root_path, 'logs')
        for file in os.listdir(log_path):
            if file.endswith('.log') and file != 'kolaycms.log':
                os.remove(os.path.join(log_path, file))
        
        # Aktivite logu oluştur
        activity = ActivityLog(
            user_id=current_user.id,
            action='Bakım yapıldı',
            details='Geçici dosyalar ve eski loglar temizlendi'
        )
        db.session.add(activity)
        db.session.commit()
        
        flash('Bakım işlemleri başarıyla tamamlandı.', 'success')
    except Exception as e:
        current_app.logger.error(f'Bakım hatası: {str(e)}')
        flash('Bakım işlemi sırasında bir hata oluştu.', 'error')
        
    return redirect(url_for('admin.settings'))

@admin_bp.route('/settings/theme', methods=['GET', 'POST'])
@login_required
@admin_required
def theme_settings():
    settings = SiteSettings.query.first()
    stats = get_admin_stats()
    
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
        db.session.commit()

    if request.method == 'POST':
        # Tema ayarlarını güncelle
        settings.primary_color = request.form.get('primary_color')
        settings.secondary_color = request.form.get('secondary_color')
        settings.is_dark_mode = 'is_dark_mode' in request.form
        settings.enable_animations = 'enable_animations' in request.form
        settings.body_bg_color = request.form.get('body_bg_color')
        settings.body_text_color = request.form.get('body_text_color')
        settings.body_link_color = request.form.get('body_link_color')
        settings.body_font_family = request.form.get('body_font_family')
        settings.body_font_size = request.form.get('body_font_size')
        settings.navbar_bg_color = request.form.get('navbar_bg_color')
        settings.navbar_text_color = request.form.get('navbar_text_color')
        settings.navbar_active_color = request.form.get('navbar_active_color')
        settings.navbar_hover_color = request.form.get('navbar_hover_color')
        settings.footer_bg_color = request.form.get('footer_bg_color')
        settings.footer_text_color = request.form.get('footer_text_color')
        settings.footer_link_color = request.form.get('footer_link_color')
        settings.banner_bg_color = request.form.get('banner_bg_color')
        settings.banner_title_color = request.form.get('banner_title_color')
        settings.banner_text_color = request.form.get('banner_text_color')
        settings.banner_button_bg_color = request.form.get('banner_button_bg_color')
        settings.banner_button_text_color = request.form.get('banner_button_text_color')
        settings.banner_button_hover_bg_color = request.form.get('banner_button_hover_bg_color')
        settings.banner_button_hover_text_color = request.form.get('banner_button_hover_text_color')
        settings.banner_indicator_color = request.form.get('banner_indicator_color')
        settings.banner_arrow_color = request.form.get('banner_arrow_color')
        settings.about_bg_color = request.form.get('about_bg_color')
        settings.about_title_color = request.form.get('about_title_color')
        settings.about_subtitle_color = request.form.get('about_subtitle_color')
        settings.about_text_color = request.form.get('about_text_color')
        settings.about_stats_number_color = request.form.get('about_stats_number_color')
        settings.about_stats_text_color = request.form.get('about_stats_text_color')
        settings.services_bg_color = request.form.get('services_bg_color')
        settings.services_title_color = request.form.get('services_title_color')
        settings.services_subtitle_color = request.form.get('services_subtitle_color')
        settings.services_card_bg_color = request.form.get('services_card_bg_color')
        settings.services_icon_color = request.form.get('services_icon_color')
        settings.services_card_title_color = request.form.get('services_card_title_color')
        settings.services_card_text_color = request.form.get('services_card_text_color')

        try:
            db.session.commit()
            flash('Tema ayarları başarıyla güncellendi.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Tema ayarları güncellenirken bir hata oluştu.', 'error')

    return render_template('admin/settings/theme.html', settings=settings, stats=stats)

@admin_bp.route('/settings/theme/reset/<section>', methods=['POST'])
@login_required
@admin_required
def theme_settings_reset_section(section):
    try:
        settings = SiteSettings.query.first()
        if settings:
            if section == 'navbar':
                # Navbar varsayılan ayarları
                settings.navbar_bg_color = '#ffffff'
                settings.navbar_text_color = '#000000'
                settings.navbar_active_color = '#007bff'
                settings.navbar_hover_color = '#0056b3'
                settings.navbar_is_fixed = True
                settings.navbar_is_transparent = False
                settings.navbar_font_family = 'inherit'
                settings.navbar_font_size = '1rem'
            
            elif section == 'body':
                # Body varsayılan ayarları
                settings.body_bg_color = '#ffffff'
                settings.body_text_color = '#212529'
                settings.body_link_color = '#007bff'
                settings.body_font_family = 'Poppins'
                settings.body_font_size = '16px'
                settings.body_heading_color = '#212529'
                settings.primary_color = '#007bff'
                settings.secondary_color = '#6c757d'
                settings.is_dark_mode = False
                settings.enable_animations = True
            
            elif section == 'banner':
                # Banner varsayılan ayarları
                settings.banner_bg_color = '#f8f9fa'
                settings.banner_title_color = '#212529'
                settings.banner_text_color = '#6c757d'
                settings.banner_button_bg_color = '#007bff'
                settings.banner_button_text_color = '#ffffff'
                settings.banner_indicator_color = '#007bff'
            
            elif section == 'about':
                # Hakkımızda varsayılan ayarları
                settings.about_bg_color = '#ffffff'
                settings.about_title_color = '#212529'
                settings.about_text_color = '#6c757d'
                settings.about_stats_number_color = '#007bff'
                settings.about_stats_text_color = '#6c757d'
                settings.about_box_bg_color = '#f8f9fa'
            
            elif section == 'services':
                # Hizmetler varsayılan ayarları
                settings.services_bg_color = '#ffffff'
                settings.services_title_color = '#212529'
                settings.services_card_bg_color = '#f8f9fa'
                settings.services_icon_color = '#007bff'
                settings.services_card_title_color = '#212529'
                settings.services_card_text_color = '#6c757d'
            
            elif section == 'blog':
                # Blog varsayılan ayarları
                settings.blog_bg_color = '#ffffff'
                settings.blog_title_color = '#212529'
                settings.blog_card_bg_color = '#f8f9fa'
                settings.blog_date_color = '#6c757d'
                settings.blog_post_title_color = '#212529'
                settings.blog_excerpt_color = '#6c757d'
            
            elif section == 'contact':
                # İletişim varsayılan ayarları
                settings.contact_bg_color = '#ffffff'
                settings.contact_title_color = '#212529'
                settings.contact_text_color = '#6c757d'
                settings.contact_form_bg_color = '#f8f9fa'
                settings.contact_button_bg_color = '#007bff'
                settings.contact_button_text_color = '#ffffff'
                settings.contact_info_bg_color = '#f8f9fa'
                settings.contact_info_border_color = '#dee2e6'
                settings.contact_info_icon_color = '#007bff'
                settings.contact_form_border_color = '#dee2e6'
                settings.contact_input_bg_color = '#ffffff'
                settings.contact_input_text_color = '#495057'
                settings.contact_input_border_color = '#ced4da'
                settings.contact_button_hover_bg_color = '#0056b3'
                settings.contact_button_hover_text_color = '#ffffff'
            
            elif section == 'video':
                # Video varsayılan ayarları
                settings.video_bg_color = '#ffffff'
                settings.video_title_color = '#212529'
                settings.video_play_button_color = '#007bff'
                settings.video_overlay_color = '#000000'
                settings.video_overlay_opacity = 50
                settings.video_play_button_bg_color = '#ffffff'
                settings.video_play_button_hover_color = '#0056b3'
                settings.video_play_button_hover_bg_color = '#ffffff'
            
            elif section == 'footer':
                # Footer varsayılan ayarları
                settings.footer_bg_color = '#212529'
                settings.footer_text_color = '#ffffff'
                settings.footer_link_color = '#ffffff'
                settings.footer_font_family = 'inherit'
                settings.footer_font_size = '1rem'
            
            db.session.commit()
            return jsonify({'status': 'success', 'message': f'{section} bölümü varsayılan ayarlara döndürüldü.'})
        
        return jsonify({'status': 'error', 'message': 'Ayarlar bulunamadı.'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@admin_bp.route('/settings/slider', methods=['GET', 'POST'])
@login_required
@admin_required
def slider_settings():
    settings = SiteSettings.query.first()
    stats = get_admin_stats()
    
    if not settings:
        settings = SiteSettings()
        db.session.add(settings)
        db.session.commit()

    if request.method == 'POST':
        # Slider ayarlarını güncelle
        settings.slider_height = request.form.get('slider_height', type=int)
        settings.slider_transition_speed = request.form.get('slider_transition_speed', type=int)
        settings.slider_animation_speed = request.form.get('slider_animation_speed', type=int)
        settings.slider_is_autoplay = 'slider_is_autoplay' in request.form
        settings.slider_show_arrows = 'slider_show_arrows' in request.form
        settings.slider_show_bullets = 'slider_show_bullets' in request.form

        try:
            db.session.commit()
            flash('Slider ayarları başarıyla güncellendi.', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Slider ayarları güncellenirken bir hata oluştu.', 'error')

    return render_template('admin/settings/slider.html', settings=settings, stats=stats)

@admin_bp.route('/settings/slider/reset', methods=['POST'])
@login_required
@admin_required
def slider_settings_reset():
    try:
        settings = SiteSettings.query.first()
        if settings:
            # Slider ayarlarını varsayılan değerlere sıfırla
            settings.slider_height = 600
            settings.slider_transition_speed = 5000
            settings.slider_animation_speed = 600
            settings.slider_is_autoplay = True
            settings.slider_show_arrows = True
            settings.slider_show_bullets = True

            db.session.commit()
            flash('Slider ayarları başarıyla varsayılan değerlere döndürüldü.', 'success')
        else:
            flash('Ayarlar bulunamadı.', 'error')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Slider ayarları sıfırlama hatası: {str(e)}')
        flash('Slider ayarları sıfırlanırken bir hata oluştu.', 'error')

    return redirect(url_for('admin.slider_settings'))

@admin_bp.route('/settings/reset', methods=['POST'])
@login_required
@admin_required
def settings_reset():
    try:
        settings = SiteSettings.query.first()
        if settings:
            # Genel site ayarlarını varsayılan değerlere döndür
            settings.site_title = 'KolayCMS'
            settings.site_description = 'Modern ve Kolay Yönetilebilir İçerik Yönetim Sistemi'
            settings.meta_keywords = 'cms, içerik yönetim sistemi, web sitesi'
            settings.footer_about = 'KolayCMS ile web sitenizi kolayca yönetin'
            settings.address = 'Örnek Adres'
            settings.phone = '+90 555 555 55 55'
            settings.email = 'info@example.com'
            settings.facebook_url = '#'
            settings.twitter_url = '#'
            settings.instagram_url = '#'
            settings.custom_css = ''
            settings.custom_js = ''
            
            # Logo ve favicon yollarını varsayılana döndür
            settings.logo_path = '/static/cobsin_template/images/logo.png'
            settings.favicon_path = '/static/cobsin_template/images/favicon.ico'
            
            db.session.commit()
            flash('Site ayarları başarıyla varsayılan değerlere döndürüldü.', 'success')
            return jsonify({'success': True}), 200
        else:
            flash('Ayarlar bulunamadı.', 'error')
            return jsonify({'success': False, 'message': 'Ayarlar bulunamadı.'}), 404
            
    except Exception as e:
        db.session.rollback()
        flash('Bir hata oluştu. Lütfen tekrar deneyin.', 'error')
        return jsonify({'success': False, 'message': str(e)}), 500

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

# Hakkımızda Bölümü
@admin_bp.route('/contents/about/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def about_edit():
    about = AboutSection.query.first()
    stats = get_admin_stats()
    
    if not about:
        # Varsayılan içeriği oluştur
        about = AboutSection(
            title="About Us",
            subtitle="It is a long established fact that a reader will be distracted by the readable content of a page when",
            content="There are many variations of passages of Lorem Ipsum available, but the majority have suffered alteration in some form, by injected humour, or randomised words",
            stats_title="Our Statistics",
            stats_content="Our achievements in numbers",
            stats_items=[
                {"number": "100+", "text": "Happy Clients"},
                {"number": "150+", "text": "Projects Completed"},
                {"number": "10+", "text": "Years Experience"},
                {"number": "24/7", "text": "Support"}
            ],
            is_active=True
        )
        db.session.add(about)
        db.session.commit()
    
    if request.method == 'POST':
        about.title = request.form.get('title')
        about.subtitle = request.form.get('subtitle')
        about.content = request.form.get('content')
        about.stats_title = request.form.get('stats_title')
        about.stats_content = request.form.get('stats_content')
        
        # İstatistikleri güncelle
        stats_count = int(request.form.get('stats_count', 0))
        stats_items = []
        for i in range(stats_count):
            number = request.form.get(f'stats_number_{i}')
            text = request.form.get(f'stats_text_{i}')
            if number and text:
                stats_items.append({"number": number, "text": text})
        about.stats_items = stats_items
        
        # Görsel yükleme
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename, {'png', 'jpg', 'jpeg', 'gif'}):
                filename = secure_filename(file.filename)
                filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], 'about', filename)
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                file.save(filepath)
                about.image_path = f'/static/uploads/about/{filename}'
        
        db.session.commit()
        flash('Hakkımızda bilgileri başarıyla güncellendi.', 'success')
        return redirect(url_for('admin.about_edit'))
    
    return render_template('admin/contents/about/edit.html', about=about, stats=stats)

# Hizmetler
@admin_bp.route('/contents/services')
@login_required
@admin_required
def services_list():
    # Eğer hiç hizmet yoksa, varsayılan hizmetleri ekle
    if Service.query.count() == 0:
        default_services = [
            {
                'title': 'Selection of Business',
                'description': 'There are many variations of passages of Lorem Ipsum available, but the form, by injected humour, or randomised',
                'icon': 'fas fa-briefcase',
                'order': 1,
                'is_active': True
            },
            {
                'title': 'Research and Analytics',
                'description': 'There are many variations of passages of Lorem Ipsum available, but the form, by injected humour, or randomised',
                'icon': 'fas fa-chart-line',
                'order': 2,
                'is_active': True
            },
            {
                'title': 'Business Plans',
                'description': 'There are many variations of passages of Lorem Ipsum available, but the form, by injected humour, or randomised',
                'icon': 'fas fa-file-alt',
                'order': 3,
                'is_active': True
            }
        ]
        
        for service_data in default_services:
            service = Service(**service_data)
            db.session.add(service)
        
        db.session.commit()
    
    services = Service.query.order_by(Service.order).all()
    stats = get_admin_stats()
    return render_template('admin/contents/services/list.html', services=services, stats=stats)

@admin_bp.route('/contents/services/create', methods=['GET', 'POST'])
@login_required
@admin_required
def services_create():
    stats = get_admin_stats()
    if request.method == 'POST':
        service = Service(
            title=request.form.get('title'),
            description=request.form.get('description'),
            icon=request.form.get('icon'),
            order=int(request.form.get('order', 0)),
            is_active=bool(request.form.get('is_active'))
        )
        
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename, {'png', 'jpg', 'jpeg', 'gif'}):
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'services', filename)
                image.save(image_path)
                service.image_path = f'/static/uploads/services/{filename}'
        
        try:
            db.session.add(service)
            db.session.commit()
            flash('Hizmet başarıyla eklendi.', 'success')
            return redirect(url_for('admin.services_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Hizmet ekleme hatası: {str(e)}')
            flash('Hizmet eklenirken bir hata oluştu.', 'error')
    
    return render_template('admin/contents/services/create.html', stats=stats)

@admin_bp.route('/contents/services/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def services_edit(id):
    stats = get_admin_stats()
    service = Service.query.get_or_404(id)
    
    if request.method == 'POST':
        service.title = request.form.get('title')
        service.description = request.form.get('description')
        service.icon = request.form.get('icon')
        service.order = int(request.form.get('order', 0))
        service.is_active = bool(request.form.get('is_active'))
        
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename, {'png', 'jpg', 'jpeg', 'gif'}):
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'services', filename)
                image.save(image_path)
                service.image_path = f'/static/uploads/services/{filename}'
        
        try:
            db.session.commit()
            flash('Hizmet başarıyla güncellendi.', 'success')
            return redirect(url_for('admin.services_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Hizmet güncelleme hatası: {str(e)}')
            flash('Hizmet güncellenirken bir hata oluştu.', 'error')
    
    return render_template('admin/contents/services/edit.html', service=service, stats=stats)

@admin_bp.route('/contents/services/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def services_delete(id):
    stats = get_admin_stats()
    service = Service.query.get_or_404(id)
    
    try:
        db.session.delete(service)
        db.session.commit()
        flash('Hizmet başarıyla silindi.', 'success')
    except Exception as e:
        current_app.logger.error(f'Hizmet silme hatası: {str(e)}')
        flash('Hizmet silinirken bir hata oluştu.', 'error')
    
    return redirect(url_for('admin.services_list'))

# Projeler
@admin_bp.route('/contents/projects')
@login_required
@admin_required
def projects_list():
    projects = Project.query.order_by(Project.order.asc()).all()
    stats = get_admin_stats()
    return render_template('admin/contents/projects/list.html', projects=projects, stats=stats)

@admin_bp.route('/contents/projects/create', methods=['GET', 'POST'])
@login_required
@admin_required
def projects_create():
    stats = get_admin_stats()
    if request.method == 'POST':
        project = Project(
            title=request.form.get('title'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            client=request.form.get('client'),
            completion_date=datetime.strptime(request.form.get('completion_date'), '%Y-%m-%d').date(),
            technologies=request.form.get('technologies'),
            project_url=request.form.get('project_url'),
            order=int(request.form.get('order', 0)),
            is_active=bool(request.form.get('is_active'))
        )
        
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename, {'png', 'jpg', 'jpeg', 'gif'}):
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'projects', filename)
                image.save(image_path)
                project.image_path = f'/static/uploads/projects/{filename}'
        
        try:
            db.session.add(project)
            db.session.commit()
            flash('Proje başarıyla eklendi.', 'success')
            return redirect(url_for('admin.projects_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Proje ekleme hatası: {str(e)}')
            flash('Proje eklenirken bir hata oluştu.', 'error')
    
    return render_template('admin/contents/projects/create.html', stats=stats)

@admin_bp.route('/contents/projects/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def projects_edit(id):
    stats = get_admin_stats()
    project = Project.query.get_or_404(id)
    
    if request.method == 'POST':
        project.title = request.form.get('title')
        project.description = request.form.get('description')
        project.category = request.form.get('category')
        project.client = request.form.get('client')
        project.completion_date = datetime.strptime(request.form.get('completion_date'), '%Y-%m-%d').date()
        project.technologies = request.form.get('technologies')
        project.project_url = request.form.get('project_url')
        project.order = int(request.form.get('order', 0))
        project.is_active = bool(request.form.get('is_active'))
        
        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename, {'png', 'jpg', 'jpeg', 'gif'}):
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'projects', filename)
                image.save(image_path)
                project.image_path = f'/static/uploads/projects/{filename}'
        
        try:
            db.session.commit()
            flash('Proje başarıyla güncellendi.', 'success')
            return redirect(url_for('admin.projects_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Proje güncelleme hatası: {str(e)}')
            flash('Proje güncellenirken bir hata oluştu.', 'error')
    
    return render_template('admin/contents/projects/edit.html', project=project, stats=stats)

@admin_bp.route('/contents/projects/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def projects_delete(id):
    stats = get_admin_stats()
    project = Project.query.get_or_404(id)
    
    try:
        db.session.delete(project)
        db.session.commit()
        flash('Proje başarıyla silindi.', 'success')
    except Exception as e:
        current_app.logger.error(f'Proje silme hatası: {str(e)}')
        flash('Proje silinirken bir hata oluştu.', 'error')
    
    return redirect(url_for('admin.projects_list'))

# Ekip Üyeleri
@admin_bp.route('/contents/team')
@login_required
@admin_required
def team_list():
    team_members = TeamMember.query.order_by(TeamMember.order.asc()).all()
    stats = get_admin_stats()
    return render_template('admin/contents/team/list.html', team_members=team_members, stats=stats)

@admin_bp.route('/contents/team/create', methods=['GET', 'POST'])
@login_required
@admin_required
def team_create():
    stats = get_admin_stats()
    if request.method == 'POST':
        member = TeamMember(
            name=request.form.get('name'),
            title=request.form.get('title'),
            bio=request.form.get('bio'),
            email=request.form.get('email'),
            phone=request.form.get('phone'),
            linkedin_url=request.form.get('linkedin_url'),
            github_url=request.form.get('github_url'),
            twitter_url=request.form.get('twitter_url'),
            order=int(request.form.get('order', 0)),
            is_active=bool(request.form.get('is_active'))
        )

        if 'image' in request.files:
            image = request.files['image']
            if image and allowed_file(image.filename, {'png', 'jpg', 'jpeg', 'gif'}):
                filename = secure_filename(image.filename)
                image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'team', filename)
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                image.save(image_path)
                member.image_path = f'/static/uploads/team/{filename}'

        try:
            db.session.add(member)
            db.session.commit()
            flash('Ekip üyesi başarıyla eklendi.', 'success')
            return redirect(url_for('admin.team_list'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Ekip üyesi ekleme hatası: {str(e)}')
            flash('Ekip üyesi eklenirken bir hata oluştu.', 'error')

    return render_template('admin/contents/team/create.html', stats=stats)

@admin_bp.route('/settings/theme/reset/all', methods=['POST'])
@login_required
@admin_required
def theme_settings_reset_all():
    try:
        settings = SiteSettings.query.first()
        if settings:
            # Navbar Ayarları
            settings.navbar_bg_color = '#ffffff'
            settings.navbar_text_color = '#000000'
            settings.navbar_active_color = '#007bff'
            settings.navbar_hover_color = '#0056b3'
            settings.navbar_is_fixed = True
            settings.navbar_is_transparent = False
            settings.navbar_font_family = 'inherit'
            settings.navbar_font_size = '1rem'
            
            # Body Ayarları
            settings.body_bg_color = '#ffffff'
            settings.body_text_color = '#212529'
            settings.body_link_color = '#007bff'
            settings.body_font_family = 'Poppins'
            settings.body_font_size = '16px'
            settings.body_heading_color = '#212529'
            settings.primary_color = '#007bff'
            settings.secondary_color = '#6c757d'
            settings.is_dark_mode = False
            settings.enable_animations = True
            
            # Banner Ayarları
            settings.banner_bg_color = '#f8f9fa'
            settings.banner_title_color = '#212529'
            settings.banner_text_color = '#6c757d'
            settings.banner_button_bg_color = '#007bff'
            settings.banner_button_text_color = '#ffffff'
            settings.banner_indicator_color = '#007bff'
            
            # Hakkımızda Ayarları
            settings.about_bg_color = '#ffffff'
            settings.about_title_color = '#212529'
            settings.about_text_color = '#6c757d'
            settings.about_stats_number_color = '#007bff'
            settings.about_stats_text_color = '#6c757d'
            settings.about_box_bg_color = '#f8f9fa'
            
            # Hizmetler Ayarları
            settings.services_bg_color = '#ffffff'
            settings.services_title_color = '#212529'
            settings.services_card_bg_color = '#f8f9fa'
            settings.services_icon_color = '#007bff'
            settings.services_card_title_color = '#212529'
            settings.services_card_text_color = '#6c757d'
            
            # Blog Ayarları
            settings.blog_bg_color = '#ffffff'
            settings.blog_title_color = '#212529'
            settings.blog_card_bg_color = '#f8f9fa'
            settings.blog_date_color = '#6c757d'
            settings.blog_post_title_color = '#212529'
            settings.blog_excerpt_color = '#6c757d'
            
            # İletişim Ayarları
            settings.contact_bg_color = '#ffffff'
            settings.contact_title_color = '#212529'
            settings.contact_text_color = '#6c757d'
            settings.contact_form_bg_color = '#f8f9fa'
            settings.contact_button_bg_color = '#007bff'
            settings.contact_button_text_color = '#ffffff'
            settings.contact_info_bg_color = '#f8f9fa'
            settings.contact_info_border_color = '#dee2e6'
            settings.contact_info_icon_color = '#007bff'
            settings.contact_form_border_color = '#dee2e6'
            settings.contact_input_bg_color = '#ffffff'
            settings.contact_input_text_color = '#495057'
            settings.contact_input_border_color = '#ced4da'
            settings.contact_button_hover_bg_color = '#0056b3'
            settings.contact_button_hover_text_color = '#ffffff'
            
            # Video Ayarları
            settings.video_bg_color = '#ffffff'
            settings.video_title_color = '#212529'
            settings.video_play_button_color = '#007bff'
            settings.video_overlay_color = '#000000'
            settings.video_overlay_opacity = 50
            settings.video_play_button_bg_color = '#ffffff'
            settings.video_play_button_hover_color = '#0056b3'
            settings.video_play_button_hover_bg_color = '#ffffff'
            
            # Footer Ayarları
            settings.footer_bg_color = '#212529'
            settings.footer_text_color = '#ffffff'
            settings.footer_link_color = '#ffffff'
            settings.footer_font_family = 'inherit'
            settings.footer_font_size = '1rem'
            
            db.session.commit()
            return jsonify({'status': 'success'})
        
        return jsonify({'status': 'error', 'message': 'Ayarlar bulunamadı.'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@admin_bp.route('/menus')
@login_required
@admin_required
def menus():
    try:
        # Tüm menüleri sıralı bir şekilde getir
        menus = Menu.query.order_by(Menu.order.asc()).all()
        stats = get_admin_stats()
        
        # Aktivite logu oluştur
        activity = ActivityLog(
            user_id=current_user.id,
            action='Menü listesi görüntülendi',
            status='info'
        )
        db.session.add(activity)
        db.session.commit()
        
        return render_template('admin/menus/index.html', menus=menus, stats=stats)
    except Exception as e:
        current_app.logger.error(f'Menü listeleme hatası: {str(e)}')
        flash('Menüler listelenirken bir hata oluştu.', 'danger')
        return redirect(url_for('admin.index'))

@admin_bp.route('/menus/create', methods=['GET', 'POST'])
@login_required
@admin_required
def menu_create():
    if request.method == 'POST':
        title = request.form.get('title')
        url = request.form.get('url')
        parent_id = request.form.get('parent_id')
        order = request.form.get('order', 0, type=int)
        is_active = request.form.get('is_active') == 'on'
        menu_type = request.form.get('menu_type', 'header')
        icon = request.form.get('icon')
        permission = request.form.get('permission')
        css_class = request.form.get('css_class')
        
        menu = Menu(
            title=title,
            url=url,
            parent_id=parent_id if parent_id else None,
            order=order,
            is_active=is_active,
            menu_type=menu_type,
            icon=icon,
            permission=permission,
            css_class=css_class
        )
        
        try:
            db.session.add(menu)
            db.session.commit()
            flash('Menü başarıyla oluşturuldu.', 'success')
            return redirect(url_for('admin.menus'))
        except Exception as e:
            db.session.rollback()
            flash('Menü oluşturulurken bir hata oluştu.', 'danger')
            current_app.logger.error(f'Menü oluşturma hatası: {str(e)}')
    
    parent_menus = Menu.query.filter_by(parent_id=None).all()
    return render_template('admin/menus/form.html', parent_menus=parent_menus)

@admin_bp.route('/menus/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def menu_edit(id):
    menu = Menu.query.get_or_404(id)
    
    if request.method == 'POST':
        menu.title = request.form.get('title')
        menu.url = request.form.get('url')
        menu.parent_id = request.form.get('parent_id') if request.form.get('parent_id') else None
        menu.order = request.form.get('order', 0, type=int)
        menu.is_active = request.form.get('is_active') == 'on'
        menu.menu_type = request.form.get('menu_type', 'header')
        menu.icon = request.form.get('icon')
        menu.permission = request.form.get('permission')
        menu.css_class = request.form.get('css_class')
        
        try:
            db.session.commit()
            flash('Menü başarıyla güncellendi.', 'success')
            return redirect(url_for('admin.menus'))
        except Exception as e:
            db.session.rollback()
            flash('Menü güncellenirken bir hata oluştu.', 'danger')
            current_app.logger.error(f'Menü güncelleme hatası: {str(e)}')
    
    parent_menus = Menu.query.filter(Menu.id != id, Menu.parent_id == None).all()
    return render_template('admin/menus/form.html', menu=menu, parent_menus=parent_menus)

@admin_bp.route('/menus/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def menu_delete(id):
    menu = Menu.query.get_or_404(id)
    
    try:
        db.session.delete(menu)
        db.session.commit()
        flash('Menü başarıyla silindi.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Menü silinirken bir hata oluştu.', 'danger')
        current_app.logger.error(f'Menü silme hatası: {str(e)}')
    
    return redirect(url_for('admin.menus'))
