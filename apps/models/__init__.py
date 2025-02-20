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
    
    # Genel ayarlar
    site_title = db.Column(db.String(100))
    site_description = db.Column(db.Text)
    logo_path = db.Column(db.String(255))
    favicon_path = db.Column(db.String(255))
    
    # Tema ayarları - Navbar
    navbar_bg_color = db.Column(db.String(7))
    navbar_text_color = db.Column(db.String(7))
    navbar_active_color = db.Column(db.String(7))
    navbar_hover_color = db.Column(db.String(7))
    navbar_is_fixed = db.Column(db.Boolean, default=False)
    navbar_is_transparent = db.Column(db.Boolean, default=False)
    
    # Tema ayarları - Genel
    body_bg_color = db.Column(db.String(7))
    body_text_color = db.Column(db.String(7))
    body_link_color = db.Column(db.String(7))
    body_font_family = db.Column(db.String(50))
    body_font_size = db.Column(db.String(10))
    primary_color = db.Column(db.String(7))
    secondary_color = db.Column(db.String(7))
    is_dark_mode = db.Column(db.Boolean, default=False)
    enable_animations = db.Column(db.Boolean, default=True)
    
    # Tema ayarları - Banner
    banner_bg_color = db.Column(db.String(7))
    banner_title_color = db.Column(db.String(7))
    banner_text_color = db.Column(db.String(7))
    banner_button_bg_color = db.Column(db.String(7))
    banner_button_text_color = db.Column(db.String(7))
    banner_indicator_color = db.Column(db.String(7))
    
    # Tema ayarları - Hakkımızda
    about_bg_color = db.Column(db.String(7))
    about_title_color = db.Column(db.String(7))
    about_text_color = db.Column(db.String(7))
    about_stats_number_color = db.Column(db.String(7))
    about_stats_text_color = db.Column(db.String(7))
    about_box_bg_color = db.Column(db.String(7))
    
    # Tema ayarları - Hizmetler
    services_bg_color = db.Column(db.String(7))
    services_title_color = db.Column(db.String(7))
    services_card_bg_color = db.Column(db.String(7))
    services_icon_color = db.Column(db.String(7))
    services_card_title_color = db.Column(db.String(7))
    services_card_text_color = db.Column(db.String(7))
    
    # Tema ayarları - Blog
    blog_bg_color = db.Column(db.String(7))
    blog_title_color = db.Column(db.String(7))
    blog_card_bg_color = db.Column(db.String(7))
    blog_date_color = db.Column(db.String(7))
    blog_post_title_color = db.Column(db.String(7))
    blog_excerpt_color = db.Column(db.String(7))
    
    # Tema ayarları - İletişim
    contact_bg_color = db.Column(db.String(7))
    contact_title_color = db.Column(db.String(7))
    contact_text_color = db.Column(db.String(7))
    contact_form_bg_color = db.Column(db.String(7))
    contact_button_bg_color = db.Column(db.String(7))
    contact_button_text_color = db.Column(db.String(7))
    
    # Tema ayarları - Video
    video_bg_color = db.Column(db.String(7))
    video_title_color = db.Column(db.String(7))
    video_play_button_color = db.Column(db.String(7))
    video_overlay_color = db.Column(db.String(7))
    video_overlay_opacity = db.Column(db.Integer)
    
    # Tema ayarları - Footer
    footer_bg_color = db.Column(db.String(7))
    footer_text_color = db.Column(db.String(7))
    footer_link_color = db.Column(db.String(7))
    
    # Özel kodlar
    custom_css = db.Column(db.Text)
    custom_js = db.Column(db.Text)
    
    # Slider ayarları
    slider_height = db.Column(db.Integer, default=600)
    slider_transition_speed = db.Column(db.Integer, default=5000)
    slider_animation_speed = db.Column(db.Integer, default=600)
    slider_is_autoplay = db.Column(db.Boolean, default=True)
    slider_show_arrows = db.Column(db.Boolean, default=True)
    slider_show_bullets = db.Column(db.Boolean, default=True)
    
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
    success_color = db.Column(db.String(10), default='#28a745', nullable=False)
    info_color = db.Column(db.String(10), default='#17a2b8', nullable=False)
    warning_color = db.Column(db.String(10), default='#ffc107', nullable=False)
    danger_color = db.Column(db.String(10), default='#dc3545', nullable=False)
    
    # Navbar Ayarları
    navbar_font_family = db.Column(db.String(50), default='inherit')
    navbar_font_size = db.Column(db.String(10), default='1rem')
    
    # Body Ayarları
    body_font_family = db.Column(db.String(50), default='Poppins, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif')
    body_font_size = db.Column(db.String(10), default='14px')
    body_line_height = db.Column(db.String(10), default='1.5')
    
    # Footer Ayarları
    footer_font_family = db.Column(db.String(50), default='inherit')
    footer_font_size = db.Column(db.String(10), default='1rem')
    footer_about = db.Column(db.Text)
    
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