from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from apps.extensions import db
import json
import os

# Model sınıfları
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(1024))
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    # Profil için ek alanlar
    first_name = db.Column(db.String(64))
    last_name = db.Column(db.String(64))
    bio = db.Column(db.Text)
    profile_picture = db.Column(db.String(255))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    @property
    def is_admin(self):
        return self.role == 'admin'

class SiteSettings(db.Model):
    __tablename__ = 'site_settings'
    id = db.Column(db.Integer, primary_key=True)
    site_title = db.Column(db.String(100), default="KolayCMS")
    site_description = db.Column(db.String(255), default="Modern ve Kolay İçerik Yönetim Sistemi")
    logo_path = db.Column(db.String(255), default="assets/img/logo.png")
    favicon_path = db.Column(db.String(255), default="assets/img/favicon.ico")
    
    # Navbar ayarları
    navbar_bg_color = db.Column(db.String(20), default="#ffffff")
    navbar_text_color = db.Column(db.String(20), default="#333333")
    navbar_active_color = db.Column(db.String(20), default="#007bff")
    navbar_hover_color = db.Column(db.String(20), default="#0056b3")
    navbar_is_fixed = db.Column(db.Boolean, default=True)
    navbar_is_transparent = db.Column(db.Boolean, default=False)
    
    # Body ayarları
    body_bg_color = db.Column(db.String(20), default="#f8f9fa")
    body_text_color = db.Column(db.String(20), default="#333333")
    body_link_color = db.Column(db.String(20), default="#007bff")
    body_font_family = db.Column(db.String(100), default="'Roboto', sans-serif")
    body_font_size = db.Column(db.String(10), default="16px")
    
    # Genel renk ayarları
    primary_color = db.Column(db.String(20), default="#007bff")
    secondary_color = db.Column(db.String(20), default="#6c757d")
    
    # Genel ayarlar
    is_dark_mode = db.Column(db.Boolean, default=False)
    enable_animations = db.Column(db.Boolean, default=True)
    
    # Tema ayarları
    theme = db.Column(db.String(50), default="default")
    # active_theme ve theme_settings alanları geçici olarak kaldırıldı
    active_theme = db.Column(db.String(50), default="default")
    theme_settings = db.Column(db.JSON)
    
    # Banner ayarları
    banner_bg_color = db.Column(db.String(20), default="#007bff")
    banner_title_color = db.Column(db.String(20), default="#ffffff")
    banner_text_color = db.Column(db.String(20), default="#ffffff")
    banner_button_bg_color = db.Column(db.String(20), default="#ffffff")
    banner_button_text_color = db.Column(db.String(20), default="#007bff")
    banner_indicator_color = db.Column(db.String(20), default="#ffffff")
    
    # About ayarları
    about_bg_color = db.Column(db.String(20), default="#ffffff")
    about_title_color = db.Column(db.String(20), default="#333333")
    about_text_color = db.Column(db.String(20), default="#6c757d")
    about_stats_number_color = db.Column(db.String(20), default="#007bff")
    about_stats_text_color = db.Column(db.String(20), default="#6c757d")
    about_box_bg_color = db.Column(db.String(20), default="#f8f9fa")
    
    # Services ayarları
    services_bg_color = db.Column(db.String(20), default="#f8f9fa")
    services_title_color = db.Column(db.String(20), default="#333333")
    services_card_bg_color = db.Column(db.String(20), default="#ffffff")
    services_icon_color = db.Column(db.String(20), default="#007bff")
    services_card_title_color = db.Column(db.String(20), default="#333333")
    services_card_text_color = db.Column(db.String(20), default="#6c757d")
    
    # Blog ayarları
    blog_bg_color = db.Column(db.String(20), default="#ffffff")
    blog_title_color = db.Column(db.String(20), default="#333333")
    blog_card_bg_color = db.Column(db.String(20), default="#f8f9fa")
    blog_date_color = db.Column(db.String(20), default="#6c757d")
    blog_post_title_color = db.Column(db.String(20), default="#333333")
    blog_excerpt_color = db.Column(db.String(20), default="#6c757d")
    
    # Contact ayarları
    contact_bg_color = db.Column(db.String(20), default="#f8f9fa")
    contact_title_color = db.Column(db.String(20), default="#333333")
    contact_text_color = db.Column(db.String(20), default="#6c757d")
    contact_form_bg_color = db.Column(db.String(20), default="#ffffff")
    contact_button_bg_color = db.Column(db.String(20), default="#007bff")
    contact_button_text_color = db.Column(db.String(20), default="#ffffff")
    
    # Video ayarları
    video_bg_color = db.Column(db.String(20), default="#000000")
    video_title_color = db.Column(db.String(20), default="#ffffff")
    video_play_button_color = db.Column(db.String(20), default="#ffffff")
    video_overlay_color = db.Column(db.String(20), default="#000000")
    video_overlay_opacity = db.Column(db.Float, default=0.5)
    
    # Footer ayarları
    footer_bg_color = db.Column(db.String(20), default="#343a40")
    footer_text_color = db.Column(db.String(20), default="#ffffff")
    footer_link_color = db.Column(db.String(20), default="#007bff")
    
    # Özel CSS ve JS
    custom_css = db.Column(db.Text, default="")
    custom_js = db.Column(db.Text, default="")
    
    # Slider ayarları
    slider_height = db.Column(db.String(10), default="500px")
    slider_transition_speed = db.Column(db.Integer, default=500)
    slider_animation_speed = db.Column(db.Integer, default=5000)
    slider_is_autoplay = db.Column(db.Boolean, default=True)
    slider_show_arrows = db.Column(db.Boolean, default=True)
    slider_show_bullets = db.Column(db.Boolean, default=True)
    
    # İletişim bilgileri
    address = db.Column(db.String(255), default="İstanbul, Türkiye")
    phone = db.Column(db.String(20), default="+90 555 123 4567")
    email = db.Column(db.String(100), default="info@kolaycms.com")
    
    # Sosyal medya
    facebook_url = db.Column(db.String(255), default="#")
    twitter_url = db.Column(db.String(255), default="#")
    instagram_url = db.Column(db.String(255), default="#")
    
    # Tema versiyonu
    theme_version = db.Column(db.String(10), default="1.0.0")
    theme_name = db.Column(db.String(50), default="KolayCMS Default")
    is_customized = db.Column(db.Boolean, default=False)
    
    # Ek renk ayarları
    success_color = db.Column(db.String(20), default="#28a745")
    info_color = db.Column(db.String(20), default="#17a2b8")
    warning_color = db.Column(db.String(20), default="#ffc107")
    danger_color = db.Column(db.String(20), default="#dc3545")
    
    # Ek font ayarları
    navbar_font_family = db.Column(db.String(100), default="'Roboto', sans-serif")
    navbar_font_size = db.Column(db.String(10), default="16px")
    body_line_height = db.Column(db.String(10), default="1.5")
    footer_font_family = db.Column(db.String(100), default="'Roboto', sans-serif")
    footer_font_size = db.Column(db.String(10), default="14px")
    
    # Footer hakkında metni
    footer_about = db.Column(db.Text, default="KolayCMS, modern ve kullanımı kolay bir içerik yönetim sistemidir.")
    
    # Bakım modu
    maintenance_mode = db.Column(db.Boolean, default=False)
    maintenance_message = db.Column(db.Text, default="Sitemiz bakımdadır. Lütfen daha sonra tekrar ziyaret edin.")
    
    # Google Analytics
    google_analytics_id = db.Column(db.String(20), default="")
    
    # reCAPTCHA
    recaptcha_site_key = db.Column(db.String(100), default="")
    recaptcha_secret_key = db.Column(db.String(100), default="")
    
    # Zaman damgaları
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SiteSettings {self.site_title}>'

class ContactInfo(db.Model):
    __tablename__ = 'contact_info'
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    working_hours = db.Column(db.String(100), nullable=True)
    google_maps_embed = db.Column(db.Text, nullable=True)
    contact_form_email = db.Column(db.String(100), nullable=True)
    whatsapp = db.Column(db.String(20), nullable=True)
    
    # Sosyal Medya Bağlantıları
    facebook = db.Column(db.String(255), nullable=True)
    twitter = db.Column(db.String(255), nullable=True)
    instagram = db.Column(db.String(255), nullable=True)
    linkedin = db.Column(db.String(255), nullable=True)
    youtube = db.Column(db.String(255), nullable=True)
    pinterest = db.Column(db.String(255), nullable=True)
    tiktok = db.Column(db.String(255), nullable=True)
    telegram = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ContactInfo {self.email}>'

class Page(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    content = db.Column(db.Text)
    meta_description = db.Column(db.String(160))
    meta_keywords = db.Column(db.String(100))
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    contact_info_id = db.Column(db.Integer, db.ForeignKey('contact_info.id'))
    contact_info = db.relationship('ContactInfo', backref=db.backref('pages', lazy=True))
    
    # Bileşik indeks
    __table_args__ = (
        db.Index('idx_page_title_is_published', 'title', 'is_published'),
    )

class Widget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text)
    settings = db.Column(db.Text)
    position = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    def get_settings(self):
        return json.loads(self.settings) if self.settings else {}
    
    def set_settings(self, settings_dict):
        self.settings = json.dumps(settings_dict)

class Menu(db.Model):
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('menus.id'))
    order = db.Column(db.Integer, default=0)
    menu_type = db.Column(db.String(20), default='header')  # header, footer, sidebar
    icon = db.Column(db.String(50))
    permission = db.Column(db.String(20))  # admin, editor, user, guest
    css_class = db.Column(db.String(100))
    settings = db.Column(db.Text)
    is_mega_menu = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    children = db.relationship('Menu', backref=db.backref('parent', remote_side=[id]))

    def __repr__(self):
        return f'<Menu {self.title}>'

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content_type = db.Column(db.String(50))  # text, image, video, etc.
    content = db.Column(db.Text)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    position = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(200))
    status = db.Column(db.String(20), default='info')  # success, error, info, warning
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='activities')
    
    def __str__(self):
        return f'{self.action} - {self.timestamp}'

class Theme(db.Model):
    __tablename__ = 'themes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    version = db.Column(db.String(20), default='1.0.0')
    author = db.Column(db.String(100), nullable=True)
    preview_image = db.Column(db.String(255), default='themes/default-preview.jpg')
    is_active = db.Column(db.Boolean, default=False)
    is_responsive = db.Column(db.Boolean, default=True)
    supports_customization = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Theme {self.name}>'

class Backup(db.Model):
    __tablename__ = 'backups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    size = db.Column(db.Integer, nullable=True)  # Boyut (byte)
    includes_uploads = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='backups')

    def __repr__(self):
        return f'<Backup {self.name}>'

# E-ticaret modelleri
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    image_path = db.Column(db.String(200))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    category = db.relationship('Category', backref='products')

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    description = db.Column(db.Text)
    
    children = db.relationship('Category', backref=db.backref('parent', remote_side=[id]))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(20), default='pending')
    total = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='orders')
    items = db.relationship('OrderItem', backref='order', lazy='dynamic')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer, default=1)
    price = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product')

class Slider(db.Model):
    __tablename__ = 'sliders'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(500))
    button_text = db.Column(db.String(100))
    button_url = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Slider {self.title}>'

class AboutSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    subtitle = db.Column(db.Text)
    content = db.Column(db.Text)
    image = db.Column(db.String(200))
    button_text = db.Column(db.String(50))
    button_url = db.Column(db.String(200))
    stats_title = db.Column(db.String(200))
    stats_content = db.Column(db.Text)
    stats_items = db.Column(db.Text)  # JSON olarak saklanacak
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_stats_items(self):
        return json.loads(self.stats_items) if self.stats_items else []

    def set_stats_items(self, items):
        self.stats_items = json.dumps(items)

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    icon = db.Column(db.String(200))
    image = db.Column(db.String(200))  # İkon yerine resim kullanmak için
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), index=True)
    content = db.Column(db.Text)
    excerpt = db.Column(db.Text)  # Kısa özet
    image = db.Column(db.String(200))
    button_text = db.Column(db.String(50))
    url = db.Column(db.String(200), index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Bileşik indeks
    __table_args__ = (
        db.Index('idx_blogpost_title_is_active', 'title', 'is_active'),
    )

class VideoSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    url = db.Column(db.String(200))
    button_text = db.Column(db.String(50))
    button_url = db.Column(db.String(200))
    thumbnail = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) 