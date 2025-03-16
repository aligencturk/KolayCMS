from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app.modules.templates.views import templates_bp
from app.models import PageTemplate, ThemeTemplate
from app.decorators import admin_required
from app import db
import uuid
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import time

# Hazır şablon HTML'leri
TEMPLATE_PRESETS = {
    'blank': {
        'html': """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }}</title>
</head>
<body>
    <header>
        <!-- Header içeriği buraya gelecek -->
    </header>
    
    <main>
        <!-- Ana içerik buraya gelecek -->
    </main>
    
    <footer>
        <!-- Footer içeriği buraya gelecek -->
    </footer>
</body>
</html>""",
        'structure': {
            'header': 'Header Bölümü',
            'main': 'Ana İçerik Bölümü',
            'footer': 'Footer Bölümü'
        }
    },
    'corporate': {
        'html': """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }} - {{ site.name }}</title>
    <link rel="stylesheet" href="{{ site.theme_url }}/css/styles.css">
</head>
<body>
    <header class="site-header">
        <div class="container">
            <div class="logo">
                <a href="{{ site.url }}">
                    <img src="{{ site.logo }}" alt="{{ site.name }}">
                </a>
            </div>
            <nav class="main-nav">
                {{ navigation.main_menu }}
            </nav>
        </div>
    </header>
    
    <main>
        <section class="hero-section">
            <div class="container">
                <h1>{{ page.hero_title|default(page.title) }}</h1>
                <p>{{ page.hero_description }}</p>
                <a href="{{ page.cta_url }}" class="button">{{ page.cta_text }}</a>
            </div>
        </section>
        
        <section class="content-section">
            <div class="container">
                {{ page.content }}
            </div>
        </section>
        
        <section class="features-section">
            <div class="container">
                <h2>{{ page.features_title }}</h2>
                <div class="features-grid">
                    {{ page.features }}
                </div>
            </div>
        </section>
    </main>
    
    <footer class="site-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-logo">
                    <img src="{{ site.footer_logo|default(site.logo) }}" alt="{{ site.name }}">
                </div>
                <div class="footer-links">
                    {{ navigation.footer_menu }}
                </div>
                <div class="footer-contact">
                    <p>{{ site.address }}</p>
                    <p>{{ site.phone }}</p>
                    <p>{{ site.email }}</p>
                </div>
            </div>
            <div class="copyright">
                <p>&copy; {{ 'now'|date('Y') }} {{ site.name }}. Tüm hakları saklıdır.</p>
            </div>
        </div>
    </footer>
</body>
</html>""",
        'structure': {
            'header': 'Üst Bölüm',
            'hero-section': 'Kahraman Bölümü',
            'content-section': 'İçerik Bölümü',
            'features-section': 'Özellikler Bölümü',
            'footer': 'Alt Bilgi Bölümü'
        }
    },
    'portfolio': {
        'html': """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }} - {{ site.name }}</title>
    <link rel="stylesheet" href="{{ site.theme_url }}/css/styles.css">
</head>
<body>
    <header class="site-header">
        <div class="container">
            <div class="logo">
                <a href="{{ site.url }}">{{ site.name }}</a>
            </div>
            <nav class="main-nav">
                {{ navigation.main_menu }}
            </nav>
        </div>
    </header>
    
    <main>
        <section class="portfolio-hero">
            <div class="container">
                <h1>{{ page.title }}</h1>
                <p>{{ page.description }}</p>
            </div>
        </section>
        
        <section class="portfolio-grid">
            <div class="container">
                {{ page.portfolio_items }}
            </div>
        </section>
        
        <section class="about-section">
            <div class="container">
                <h2>{{ page.about_title }}</h2>
                {{ page.about_content }}
            </div>
        </section>
    </main>
    
    <footer class="site-footer">
        <div class="container">
            <div class="social-links">
                {{ social_links }}
            </div>
            <div class="copyright">
                <p>&copy; {{ 'now'|date('Y') }} {{ site.name }}. Tüm hakları saklıdır.</p>
            </div>
        </div>
    </footer>
</body>
</html>""",
        'structure': {
            'header': 'Üst Bölüm',
            'portfolio-hero': 'Portfolyo Başlığı',
            'portfolio-grid': 'Portfolyo Öğeleri',
            'about-section': 'Hakkımda Bölümü',
            'footer': 'Alt Bilgi Bölümü'
        }
    },
    'blog': {
        'html': """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }} - {{ site.name }}</title>
    <link rel="stylesheet" href="{{ site.theme_url }}/css/styles.css">
</head>
<body>
    <header class="site-header">
        <div class="container">
            <div class="logo">
                <a href="{{ site.url }}">{{ site.name }}</a>
            </div>
            <nav class="main-nav">
                {{ navigation.main_menu }}
            </nav>
        </div>
    </header>
    
    <main class="blog-layout">
        <div class="container">
            <div class="content-area">
                <article class="blog-post">
                    <header class="post-header">
                        <h1>{{ page.title }}</h1>
                        <div class="post-meta">
                            <span class="post-date">{{ page.date }}</span>
                            <span class="post-author">{{ page.author }}</span>
                            <span class="post-categories">{{ page.categories }}</span>
                        </div>
                    </header>
                    
                    <div class="post-content">
                        {{ page.content }}
                    </div>
                    
                    <footer class="post-footer">
                        <div class="post-tags">
                            {{ page.tags }}
                        </div>
                        <div class="post-share">
                            {{ social_share }}
                        </div>
                    </footer>
                </article>
                
                <div class="post-navigation">
                    <div class="prev-post">
                        {{ previous_post }}
                    </div>
                    <div class="next-post">
                        {{ next_post }}
                    </div>
                </div>
                
                <div class="comments-section">
                    {{ comments }}
                </div>
            </div>
            
            <aside class="sidebar">
                <div class="widget widget-about">
                    {{ about_widget }}
                </div>
                <div class="widget widget-recent-posts">
                    {{ recent_posts_widget }}
                </div>
                <div class="widget widget-categories">
                    {{ categories_widget }}
                </div>
                <div class="widget widget-tags">
                    {{ tags_widget }}
                </div>
            </aside>
        </div>
    </main>
    
    <footer class="site-footer">
        <div class="container">
            <div class="footer-widgets">
                {{ footer_widgets }}
            </div>
            <div class="copyright">
                <p>&copy; {{ 'now'|date('Y') }} {{ site.name }}. Tüm hakları saklıdır.</p>
            </div>
        </div>
    </footer>
</body>
</html>""",
        'structure': {
            'header': 'Üst Bölüm',
            'content-area': 'İçerik Alanı',
            'post-header': 'Yazı Başlığı',
            'post-content': 'Yazı İçeriği',
            'post-footer': 'Yazı Alt Bilgisi',
            'post-navigation': 'Yazı Navigasyonu',
            'comments-section': 'Yorum Bölümü',
            'sidebar': 'Kenar Çubuğu',
            'footer': 'Alt Bilgi Bölümü'
        }
    },
    'ecommerce': {
        'html': """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }} - {{ site.name }}</title>
    <link rel="stylesheet" href="{{ site.theme_url }}/css/styles.css">
</head>
<body>
    <header class="site-header">
        <div class="container">
            <div class="header-top">
                <div class="contact-info">
                    <span><i class="icon-phone"></i> {{ site.phone }}</span>
                    <span><i class="icon-email"></i> {{ site.email }}</span>
                </div>
                <div class="user-actions">
                    <a href="{{ url('account') }}">Hesabım</a>
                    <a href="{{ url('wishlist') }}">Favoriler</a>
                    <a href="{{ url('cart') }}">Sepet ({{ cart.count }})</a>
                </div>
            </div>
            
            <div class="header-main">
                <div class="logo">
                    <a href="{{ site.url }}">
                        <img src="{{ site.logo }}" alt="{{ site.name }}">
                    </a>
                </div>
                
                <div class="search-form">
                    {{ search_form }}
                </div>
                
                <div class="mini-cart">
                    {{ mini_cart }}
                </div>
            </div>
            
            <nav class="main-nav">
                {{ navigation.main_menu }}
            </nav>
        </div>
    </header>
    
    <main>
        <section class="product-showcase">
            <div class="container">
                <h1>{{ page.title }}</h1>
                
                <div class="product-grid">
                    {{ page.featured_products }}
                </div>
            </div>
        </section>
        
        <section class="categories-section">
            <div class="container">
                <h2>{{ page.categories_title }}</h2>
                <div class="categories-grid">
                    {{ page.product_categories }}
                </div>
            </div>
        </section>
        
        <section class="promo-section">
            <div class="container">
                {{ page.promotions }}
            </div>
        </section>
    </main>
    
    <footer class="site-footer">
        <div class="container">
            <div class="footer-top">
                <div class="footer-about">
                    <h3>{{ site.name }} Hakkında</h3>
                    <p>{{ site.description }}</p>
                </div>
                
                <div class="footer-links">
                    <h3>Hızlı Bağlantılar</h3>
                    {{ navigation.footer_menu }}
                </div>
                
                <div class="footer-categories">
                    <h3>Kategoriler</h3>
                    {{ navigation.categories_menu }}
                </div>
                
                <div class="footer-contact">
                    <h3>İletişim</h3>
                    <p>{{ site.address }}</p>
                    <p>{{ site.phone }}</p>
                    <p>{{ site.email }}</p>
                </div>
            </div>
            
            <div class="footer-bottom">
                <div class="copyright">
                    <p>&copy; {{ 'now'|date('Y') }} {{ site.name }}. Tüm hakları saklıdır.</p>
                </div>
                
                <div class="payment-methods">
                    {{ payment_methods }}
                </div>
            </div>
        </div>
    </footer>
</body>
</html>""",
        'structure': {
            'header': 'Üst Bölüm',
            'header-top': 'Üst Bölüm - Üst',
            'header-main': 'Üst Bölüm - Ana',
            'product-showcase': 'Ürün Vitrini',
            'categories-section': 'Kategoriler Bölümü',
            'promo-section': 'Promosyon Bölümü',
            'footer': 'Alt Bilgi Bölümü',
            'footer-top': 'Alt Bilgi - Üst',
            'footer-bottom': 'Alt Bilgi - Alt'
        }
    },
    'event': {
        'html': """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }} - {{ site.name }}</title>
    <link rel="stylesheet" href="{{ site.theme_url }}/css/styles.css">
</head>
<body>
    <header class="site-header">
        <div class="container">
            <div class="logo">
                <a href="{{ site.url }}">
                    <img src="{{ site.logo }}" alt="{{ site.name }}">
                </a>
            </div>
            <nav class="main-nav">
                {{ navigation.main_menu }}
            </nav>
        </div>
    </header>
    
    <main>
        <section class="event-hero">
            <div class="container">
                <div class="event-info">
                    <h1>{{ page.title }}</h1>
                    <p class="event-date">{{ page.event_date }}</p>
                    <p class="event-location">{{ page.event_location }}</p>
                    <div class="event-cta">
                        <a href="{{ page.ticket_url }}" class="button">{{ page.ticket_text|default('Bilet Al') }}</a>
                    </div>
                </div>
                <div class="event-countdown">
                    {{ event_countdown }}
                </div>
            </div>
        </section>
        
        <section class="event-details">
            <div class="container">
                <h2>Etkinlik Hakkında</h2>
                <div class="event-description">
                    {{ page.event_description }}
                </div>
            </div>
        </section>
        
        <section class="event-schedule">
            <div class="container">
                <h2>Program</h2>
                <div class="schedule-table">
                    {{ page.event_schedule }}
                </div>
            </div>
        </section>
        
        <section class="event-speakers">
            <div class="container">
                <h2>Konuşmacılar</h2>
                <div class="speakers-grid">
                    {{ page.event_speakers }}
                </div>
            </div>
        </section>
        
        <section class="event-sponsors">
            <div class="container">
                <h2>Sponsorlar</h2>
                <div class="sponsors-grid">
                    {{ page.event_sponsors }}
                </div>
            </div>
        </section>
        
        <section class="event-venue">
            <div class="container">
                <h2>Mekan</h2>
                <div class="venue-info">
                    <div class="venue-details">
                        <h3>{{ page.venue_name }}</h3>
                        <p>{{ page.venue_address }}</p>
                        <div class="venue-directions">
                            {{ page.venue_directions }}
                        </div>
                    </div>
                    <div class="venue-map">
                        {{ venue_map }}
                    </div>
                </div>
            </div>
        </section>
    </main>
    
    <footer class="site-footer">
        <div class="container">
            <div class="social-links">
                {{ social_links }}
            </div>
            <div class="contact-info">
                <p>{{ site.email }}</p>
                <p>{{ site.phone }}</p>
            </div>
            <div class="copyright">
                <p>&copy; {{ 'now'|date('Y') }} {{ site.name }}. Tüm hakları saklıdır.</p>
            </div>
        </div>
    </footer>
</body>
</html>""",
        'structure': {
            'header': 'Üst Bölüm',
            'event-hero': 'Etkinlik Banner',
            'event-details': 'Etkinlik Detayları',
            'event-schedule': 'Etkinlik Programı',
            'event-speakers': 'Konuşmacılar',
            'event-sponsors': 'Sponsorlar',
            'event-venue': 'Etkinlik Mekanı',
            'footer': 'Alt Bilgi Bölümü'
        }
    }
}

@templates_bp.route('/')
@login_required
@admin_required
def index():
    """Sayfa şablonlarını listele"""
    templates_ref = db.collection('page_templates').stream()
    templates = []
    for doc in templates_ref:
        template_data = doc.to_dict()
        # id zaten template_data içinde varsa, onu kullanma
        if 'id' in template_data:
            templates.append(PageTemplate(**template_data))
        else:
            templates.append(PageTemplate(**template_data, id=doc.id))
    return render_template('templates/index.html', templates=templates)

@templates_bp.route('/create', methods=['GET'])
@login_required
@admin_required
def create():
    """Yeni şablon oluştur - Doğrudan görsel editöre yönlendir"""
    # Boş şablon oluştur
    template_id = str(uuid.uuid4())
    
    # Varsayılan şablon verilerini hazırla
    selected_template = TEMPLATE_PRESETS.get('blank', TEMPLATE_PRESETS['blank'])
    html_content = selected_template['html']
    available_slots = selected_template['structure']
    
    # Şablon nesnesi oluştur
    template = PageTemplate(
        id=template_id,
        name=f"Yeni Şablon {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        description="Bu şablon otomatik olarak oluşturuldu. Düzenleyicide değişiklik yapabilirsiniz.",
        template_type="page",
        html_structure=html_content,
        available_slots=available_slots,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=current_user.id,
        updated_by=current_user.id,
        thumbnail_url=None
    )
    
    # Veritabanına kaydet
    db.collection('page_templates').document(template_id).set(template.to_dict())
    
    # Görsel düzenleyiciye yönlendir
    return redirect(url_for('themes.visual_editor', template_id=template_id))

@templates_bp.route('/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_template():
    """Şablon yükle"""
    if request.method == 'POST':
        if 'template_file' not in request.files:
            flash('Dosya seçilmedi', 'error')
            return redirect(request.url)
            
        template_file = request.files['template_file']
        
        if template_file.filename == '':
            flash('Dosya seçilmedi', 'error')
            return redirect(request.url)
            
        if template_file:
            # Dosya adını güvenli hale getir
            filename = secure_filename(template_file.filename)
            
            # Dosyayı kontrol et ve içeriği oku
            if filename.endswith('.html') or filename.endswith('.htm'):
                html_content = template_file.read().decode('utf-8')
                
                # Yeni şablon oluştur
                template_id = str(uuid.uuid4())
                template = PageTemplate(
                    id=template_id,
                    name=request.form.get('name', f"Yüklenen Şablon {datetime.now().strftime('%d.%m.%Y %H:%M')}"),
                    description=request.form.get('description', "Bu şablon dosyadan yüklendi."),
                    template_type=request.form.get('template_type', 'page'),
                    html_structure=html_content,
                    available_slots={"content": "Ana İçerik Alanı"},  # Varsayılan slot
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    created_by=current_user.id,
                    updated_by=current_user.id,
                    thumbnail_url=None
                )
                
                # Veritabanına kaydet
                db.collection('page_templates').document(template_id).set(template.to_dict())
                
                flash('Şablon başarıyla yüklendi', 'success')
                return redirect(url_for('themes.visual_editor', template_id=template_id))
            else:
                flash('Sadece HTML dosyaları kabul edilir', 'error')
                return redirect(request.url)
    
    return render_template('templates/upload.html')

@templates_bp.route('/<template_id>')
@login_required
@admin_required
def view(template_id):
    """Şablon detaylarını görüntüle"""
    template_ref = db.collection('page_templates').document(template_id).get()
    if not template_ref.exists:
        flash('Şablon bulunamadı', 'error')
        return redirect(url_for('templates.index'))
        
    template = PageTemplate(**template_ref.to_dict(), id=template_ref.id)
    return render_template('templates/view.html', template=template)

@templates_bp.route('/<template_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(template_id):
    """Şablon düzenle"""
    template_ref = db.collection('page_templates').document(template_id).get()
    if not template_ref.exists:
        flash('Şablon bulunamadı', 'error')
        return redirect(url_for('templates.index'))
        
    template_data = template_ref.to_dict()
    
    # Sistem şablonunu düzenlemeyi engelle
    if template_data.get('is_system', False):
        flash('Sistem şablonları düzenlenemez', 'error')
        return redirect(url_for('templates.index'))
    
    if request.method == 'POST':
        # Form verilerini al
        name = request.form.get('name')
        description = request.form.get('description')
        template_type = request.form.get('template_type')
        html_structure = request.form.get('html_structure')
        
        # Thumbnail işlemleri
        thumbnail_url = template_data.get('thumbnail_url')
        
        # Mevcut görseli kaldır işaretlendiyse
        if request.form.get('remove_thumbnail'):
            thumbnail_url = None
        
        # Yeni görsel yüklendiyse
        if 'thumbnail' in request.files and request.files['thumbnail'].filename:
            thumbnail = request.files['thumbnail']
            filename = secure_filename(f"{str(uuid.uuid4())}-{thumbnail.filename}")
            upload_folder = os.path.join(current_app.root_path, 'static/uploads/templates')
            
            # Klasör yoksa oluştur
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            # Dosyayı kaydet
            thumbnail_path = os.path.join(upload_folder, filename)
            thumbnail.save(thumbnail_path)
            thumbnail_url = f"/static/uploads/templates/{filename}"
        
        # Slot bilgilerini işle (eğer varsa)
        available_slots = template_data.get('available_slots', {})
        if 'slot_key' in request.form:
            available_slots = {}
            slot_keys = request.form.getlist('slot_key')
            slot_names = request.form.getlist('slot_name')
            
            for i in range(len(slot_keys)):
                if slot_keys[i] and slot_names[i]:
                    available_slots[slot_keys[i]] = slot_names[i]
        
        # Veritabanını güncelle
        update_data = {
            'name': name,
            'description': description,
            'template_type': template_type,
            'html_structure': html_structure,
            'available_slots': available_slots,
            'updated_at': datetime.now(),
            'updated_by': current_user.id
        }
        
        # Thumbnail varsa ekle
        if thumbnail_url is not None:
            update_data['thumbnail_url'] = thumbnail_url
        
        db.collection('page_templates').document(template_id).update(update_data)
        
        flash('Şablon başarıyla güncellendi', 'success')
        return redirect(url_for('templates.view', template_id=template_id))
        
    template = PageTemplate(**template_data, id=template_id)
    return render_template('templates/edit.html', template=template)

@templates_bp.route('/<template_id>/duplicate', methods=['POST'])
@login_required
@admin_required
def duplicate(template_id):
    """Şablonu kopyala"""
    template_ref = db.collection('page_templates').document(template_id).get()
    if not template_ref.exists:
        flash('Şablon bulunamadı', 'error')
        return redirect(url_for('templates.index'))
        
    template_data = template_ref.to_dict()
    
    # Yeni şablon oluştur
    new_template = PageTemplate(
        name=f"{template_data.get('name')} - Kopya",
        description=template_data.get('description'),
        template_type=template_data.get('template_type'),
        html_structure=template_data.get('html_structure'),
        available_slots=template_data.get('available_slots', {}),
        thumbnail_url=template_data.get('thumbnail_url'),
        is_system=False,
        id=str(uuid.uuid4()),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by=current_user.id,
        updated_by=current_user.id
    )
    
    # Firestore'a kaydet
    db.collection('page_templates').document(new_template.id).set(new_template.to_dict())
    
    flash('Şablon başarıyla kopyalandı', 'success')
    return redirect(url_for('templates.index'))

@templates_bp.route('/<template_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(template_id):
    """Şablonu sil"""
    # Sistem şablonunu silmeyi engelle
    template_ref = db.collection('page_templates').document(template_id).get()
    if template_ref.exists and template_ref.to_dict().get('is_system', False):
        flash('Sistem şablonları silinemez', 'error')
        return redirect(url_for('templates.index'))
    
    # Değilse sil
    db.collection('page_templates').document(template_id).delete()
    
    flash('Şablon başarıyla silindi', 'success')
    return redirect(url_for('templates.index')) 