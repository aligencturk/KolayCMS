from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from apps.models import Page, BlogPost, Slide, Service, AboutSection, VideoSection, SiteSettings, ContactInfo, db, Menu
from apps.forms import ContactForm
from datetime import datetime

main_bp = Blueprint('main', __name__)

def get_template(page):
    """Sayfa şablonunu belirle"""
    templates = {
        'default': 'main/templates/default.html',
        'full-width': 'main/templates/full-width.html',
        'sidebar': 'main/templates/sidebar.html',
        'landing': 'main/templates/landing.html'
    }
    return templates.get(page.template, 'main/templates/default.html')

@main_bp.context_processor
def utility_processor():
    """Global template değişkenlerini sağla"""
    # Her seferinde yeni bir sorgu yap
    db.session.expire_all()
    db.session.commit()
    
    # Yeni bir sorgu ile en güncel ayarları al
    settings = db.session.query(SiteSettings).first()
    if not settings:
        settings = SiteSettings(
            site_title='KolayCMS',
            navbar_bg_color='#ffffff',
            navbar_text_color='#000000',
            navbar_active_color='#007bff',
            navbar_hover_color='#0056b3',
            body_bg_color='#ffffff',
            body_text_color='#212529',
            body_link_color='#007bff',
            footer_bg_color='#343a40',
            footer_text_color='#ffffff',
            footer_link_color='#ffffff'
        )
        db.session.add(settings)
        try:
            db.session.commit()
        except:
            db.session.rollback()
    
    contact_info = ContactInfo.query.first()
    
    # Menü öğelerini getir
    menus = [
        {'title': 'Ana Sayfa', 'url': url_for('main.index')},
        {'title': 'Hakkımızda', 'url': url_for('main.about')},
        {'title': 'Hizmetler', 'url': url_for('main.services')},
        {'title': 'Blog', 'url': url_for('main.blog')},
        {'title': 'İletişim', 'url': url_for('main.contact')}
    ]
    
    return {
        'now': datetime.now(),
        'settings': settings,
        'contact_info': contact_info,
        'menus': menus
    }

@main_bp.route('/')
def index():
    # Ana sayfayı getir
    home_page = Page.query.filter_by(slug='home', is_published=True).first()
    
    # Diğer içerikleri getir
    slides = Slide.query.filter_by(is_active=True).order_by(Slide.order).all()
    about = AboutSection.query.filter_by(is_active=True).first()
    services = Service.query.filter_by(is_active=True).order_by(Service.order).all()
    blog_posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).limit(3).all()
    video = VideoSection.query.filter_by(is_active=True).first()
    
    if home_page:
        # Şablona göre render et
        template = get_template(home_page)
        return render_template(template,
                            page=home_page,
                            slides=slides,
                            about=about,
                            services=services,
                            blog_posts=blog_posts,
                            video=video)
    
    # Ana sayfa yoksa varsayılan şablonu kullan
    return render_template('main/templates/default.html',
                        slides=slides,
                        about=about,
                        services=services,
                        blog_posts=blog_posts,
                        video=video)

@main_bp.route('/page/<slug>')
def page(slug):
    try:
        page = Page.query.filter_by(slug=slug, is_published=True).first_or_404()
        template = get_template(page)
        return render_template(template, page=page)
    except Exception as e:
        current_app.logger.error(f"Sayfa görüntülenirken hata oluştu: {str(e)}")
        return render_template('main/error.html', error="Sayfa bulunamadı"), 404

@main_bp.route('/blog')
def blog():
    page = request.args.get('page', 1, type=int)
    per_page = 9
    
    posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc())
    pagination = posts.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('main/blog.html',
                         posts=pagination.items,
                         pagination=pagination)

@main_bp.route('/blog/<slug>')
def blog_detail(slug):
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    return render_template('main/blog_detail.html', post=post)

@main_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()
    page = Page.query.filter_by(slug='contact', is_published=True).first()
    contact_info = ContactInfo.query.first()
    
    if form.validate_on_submit():
        # Form verilerini al
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        message = form.message.data
        
        # Burada form verilerini işleyebilirsiniz
        # Örneğin: E-posta gönderme, veritabanına kaydetme vb.
        
        flash('Mesajınız başarıyla gönderildi! En kısa sürede size dönüş yapacağız.', 'success')
        return redirect(url_for('main.contact'))
        
    return render_template('main/contact.html', 
                         form=form, 
                         page=page,
                         contact_info=contact_info)

@main_bp.route('/about')
def about():
    about = AboutSection.query.first()
    return render_template('main/about.html', about=about)

@main_bp.route('/services')
def services():
    services = Service.query.filter_by(is_active=True).order_by(Service.order).all()
    page = Page.query.filter_by(slug='services').first()
    return render_template('main/services.html', services=services, page=page)

@main_bp.route('/events')
@login_required
def events():
    return render_template('main/events.html') 