from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from apps.extensions import db

# Kullanıcı modeli
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(1024))
    role = db.Column(db.String(20), default='user')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    last_login = db.Column(db.DateTime)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __str__(self):
        return self.username

# Site ayarları modeli
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

# Aktivite günlüğü modeli
class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(200))
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', backref='activities')

# Diğer modelleri içe aktar
from .page import Page
from .content import Content
from .widget import Widget
from .menu import Menu
from .theme import Theme
from .shop import Product, Category
from .order import Order
from .content_types import Slide, AboutSection, Service, BlogPost, VideoSection, Project, TeamMember, Testimonial, ContactInfo 