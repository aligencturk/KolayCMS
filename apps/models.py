from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
from flask_sqlalchemy import SQLAlchemy
import json
import os
from apps import db

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
    
    # Genel Ayarlar
    site_title = db.Column(db.String(100), default='KolayCMS')
    site_description = db.Column(db.Text)
    meta_keywords = db.Column(db.String(200))
    logo_path = db.Column(db.String(200))
    favicon_path = db.Column(db.String(200))
    
    # İletişim Bilgileri
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    facebook_url = db.Column(db.String(200))
    twitter_url = db.Column(db.String(200))
    instagram_url = db.Column(db.String(200))
    
    # Tema Ayarları
    theme_version = db.Column(db.String(10), default='1.0')
    theme_name = db.Column(db.String(50), default='default')
    is_customized = db.Column(db.Boolean, default=False)
    primary_color = db.Column(db.String(10), default='#007bff', nullable=False)
    secondary_color = db.Column(db.String(10), default='#6c757d', nullable=False)
    success_color = db.Column(db.String(10), default='#28a745', nullable=False)
    info_color = db.Column(db.String(10), default='#17a2b8', nullable=False)
    warning_color = db.Column(db.String(10), default='#ffc107', nullable=False)
    danger_color = db.Column(db.String(10), default='#dc3545', nullable=False)
    
    # Navbar Ayarları
    navbar_bg_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    navbar_text_color = db.Column(db.String(10), default='#000000', nullable=False)
    navbar_active_color = db.Column(db.String(10), default='#007bff', nullable=False)
    navbar_hover_color = db.Column(db.String(10), default='#0056b3', nullable=False)
    navbar_is_fixed = db.Column(db.Boolean, default=True)
    navbar_is_transparent = db.Column(db.Boolean, default=False)
    navbar_font_family = db.Column(db.String(50), default='inherit')
    navbar_font_size = db.Column(db.String(10), default='1rem')
    
    # Body Ayarları
    body_bg_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    body_text_color = db.Column(db.String(10), default='#212529', nullable=False)
    body_link_color = db.Column(db.String(10), default='#007bff', nullable=False)
    body_font_family = db.Column(db.String(50), default='Poppins, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif')
    body_font_size = db.Column(db.String(10), default='14px')
    body_line_height = db.Column(db.String(10), default='1.5')
    
    # Banner/Slider Ayarları
    banner_bg_color = db.Column(db.String(10), default='#f8f9fa', nullable=False)
    banner_title_color = db.Column(db.String(10), default='#212529', nullable=False)
    banner_text_color = db.Column(db.String(10), default='#6c757d', nullable=False)
    banner_button_bg_color = db.Column(db.String(10), default='#007bff', nullable=False)
    banner_button_text_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    banner_button_hover_bg_color = db.Column(db.String(10), default='#0056b3', nullable=False)
    banner_button_hover_text_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    banner_indicator_color = db.Column(db.String(10), default='#007bff', nullable=False)
    banner_arrow_color = db.Column(db.String(10), default='#007bff', nullable=False)
    
    # Hakkımızda Ayarları
    about_bg_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    about_title_color = db.Column(db.String(10), default='#212529', nullable=False)
    about_subtitle_color = db.Column(db.String(10), default='#6c757d', nullable=False)
    about_text_color = db.Column(db.String(10), default='#212529', nullable=False)
    about_stats_number_color = db.Column(db.String(10), default='#007bff', nullable=False)
    about_stats_text_color = db.Column(db.String(10), default='#6c757d', nullable=False)
    about_box_bg_color = db.Column(db.String(10), default='#f8f9fa', nullable=False)
    about_box_border_color = db.Column(db.String(10), default='#dee2e6', nullable=False)
    
    # Hizmetler Ayarları
    services_bg_color = db.Column(db.String(10), default='#f8f9fa', nullable=False)
    services_title_color = db.Column(db.String(10), default='#212529', nullable=False)
    services_subtitle_color = db.Column(db.String(10), default='#6c757d', nullable=False)
    services_card_bg_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    services_card_border_color = db.Column(db.String(10), default='#dee2e6', nullable=False)
    services_icon_color = db.Column(db.String(10), default='#007bff', nullable=False)
    services_icon_bg_color = db.Column(db.String(10), default='#e9ecef', nullable=False)
    services_card_title_color = db.Column(db.String(10), default='#212529', nullable=False)
    services_card_text_color = db.Column(db.String(10), default='#6c757d', nullable=False)
    services_card_hover_shadow = db.Column(db.String(10), default='rgba(0,0,0,0.1)', nullable=False)
    
    # Blog Ayarları
    blog_bg_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    blog_title_color = db.Column(db.String(10), default='#212529', nullable=False)
    blog_subtitle_color = db.Column(db.String(10), default='#6c757d', nullable=False)
    blog_card_bg_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    blog_card_border_color = db.Column(db.String(10), default='#dee2e6', nullable=False)
    blog_date_color = db.Column(db.String(10), default='#6c757d', nullable=False)
    blog_post_title_color = db.Column(db.String(10), default='#212529', nullable=False)
    blog_excerpt_color = db.Column(db.String(10), default='#6c757d', nullable=False)
    blog_card_hover_shadow = db.Column(db.String(10), default='rgba(0,0,0,0.1)', nullable=False)
    
    # İletişim Ayarları
    contact_bg_color = db.Column(db.String(10), default='#f8f9fa', nullable=False)
    contact_title_color = db.Column(db.String(10), default='#212529', nullable=False)
    contact_subtitle_color = db.Column(db.String(10), default='#6c757d', nullable=False)
    contact_text_color = db.Column(db.String(10), default='#212529', nullable=False)
    contact_info_bg_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    contact_info_border_color = db.Column(db.String(10), default='#dee2e6', nullable=False)
    contact_info_icon_color = db.Column(db.String(10), default='#007bff', nullable=False)
    contact_form_bg_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    contact_form_border_color = db.Column(db.String(10), default='#dee2e6', nullable=False)
    contact_input_bg_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    contact_input_text_color = db.Column(db.String(10), default='#212529', nullable=False)
    contact_input_border_color = db.Column(db.String(10), default='#ced4da', nullable=False)
    contact_button_bg_color = db.Column(db.String(10), default='#007bff', nullable=False)
    contact_button_text_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    contact_button_hover_bg_color = db.Column(db.String(10), default='#0056b3', nullable=False)
    contact_button_hover_text_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    
    # Video Ayarları
    video_bg_color = db.Column(db.String(10), default='#f8f9fa', nullable=False)
    video_overlay_color = db.Column(db.String(20), default='rgba(0,0,0,0.5)', nullable=False)
    video_title_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    video_subtitle_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    video_play_button_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    video_play_button_bg_color = db.Column(db.String(10), default='#007bff', nullable=False)
    video_play_button_hover_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    video_play_button_hover_bg_color = db.Column(db.String(10), default='#0056b3', nullable=False)
    
    # Footer Ayarları
    footer_bg_color = db.Column(db.String(10), default='#343a40', nullable=False)
    footer_text_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    footer_link_color = db.Column(db.String(10), default='#ffffff', nullable=False)
    footer_font_family = db.Column(db.String(50), default='inherit')
    footer_font_size = db.Column(db.String(10), default='1rem')
    footer_about = db.Column(db.Text)
    
    # Özel Kodlar
    custom_css = db.Column(db.Text)
    custom_js = db.Column(db.Text)
    custom_header_code = db.Column(db.Text)
    custom_footer_code = db.Column(db.Text)
    custom_meta_tags = db.Column(db.Text)
    
    # Diğer Ayarlar
    maintenance_mode = db.Column(db.Boolean, default=False)
    maintenance_message = db.Column(db.Text, default='Site bakım modunda.')
    google_analytics_id = db.Column(db.String(50))
    recaptcha_site_key = db.Column(db.String(100))
    recaptcha_secret_key = db.Column(db.String(100))
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<SiteSettings {self.id}>'

class ContactInfo(db.Model):
    __tablename__ = 'contact_info'
    
    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(200))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    google_maps_embed = db.Column(db.Text)
    working_hours = db.Column(db.String(200))
    facebook = db.Column(db.String(200))
    twitter = db.Column(db.String(200))
    instagram = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Page(db.Model):
    __tablename__ = 'pages'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    content = db.Column(db.Text)
    meta_description = db.Column(db.String(160))
    meta_keywords = db.Column(db.String(100))
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    contact_info_id = db.Column(db.Integer, db.ForeignKey('contact_info.id'))
    contact_info = db.relationship('ContactInfo', backref=db.backref('pages', lazy=True))

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
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('menu.id'))
    url = db.Column(db.String(200))
    position = db.Column(db.Integer, default=0)
    settings = db.Column(db.Text)
    is_mega_menu = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    children = db.relationship('Menu', backref=db.backref('parent', remote_side=[id]))

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content_type = db.Column(db.String(50))  # text, image, video, etc.
    content = db.Column(db.Text)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'))
    position = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ActivityLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(200))
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='activities')
    
    def __str__(self):
        return f"{self.action} - {self.timestamp}"

class Theme(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    template = db.Column(db.Text)
    css = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=False)

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

class Slide(db.Model):
    __tablename__ = 'slides'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(500), nullable=True)
    button1_text = db.Column(db.String(100))
    button1_url = db.Column(db.String(200))
    button2_text = db.Column(db.String(100))
    button2_url = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

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
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

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
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    excerpt = db.Column(db.Text)  # Kısa özet
    image = db.Column(db.String(200))
    button_text = db.Column(db.String(50))
    url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    is_active = db.Column(db.Boolean, default=True)

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