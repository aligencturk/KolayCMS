from datetime import datetime
from apps import db

class Settings(db.Model):
    __tablename__ = 'settings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Genel Ayarlar
    site_title = db.Column(db.String(100), nullable=False, default='KolayCMS')
    site_description = db.Column(db.String(255))
    meta_keywords = db.Column(db.String(255))
    meta_description = db.Column(db.String(255))
    
    # Logo ve Favicon
    logo_path = db.Column(db.String(255))
    favicon_path = db.Column(db.String(255))
    
    # İletişim Bilgileri
    contact_email = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    contact_address = db.Column(db.Text)
    contact_map = db.Column(db.Text)
    
    # Sosyal Medya
    facebook_url = db.Column(db.String(255))
    twitter_url = db.Column(db.String(255))
    instagram_url = db.Column(db.String(255))
    linkedin_url = db.Column(db.String(255))
    youtube_url = db.Column(db.String(255))
    
    # SMTP Ayarları
    smtp_host = db.Column(db.String(100))
    smtp_port = db.Column(db.Integer)
    smtp_user = db.Column(db.String(100))
    smtp_pass = db.Column(db.String(100))
    smtp_from_name = db.Column(db.String(100))
    smtp_from_email = db.Column(db.String(100))
    
    # Özel Kodlar
    google_analytics = db.Column(db.Text)
    facebook_pixel = db.Column(db.Text)
    custom_css = db.Column(db.Text)
    custom_js = db.Column(db.Text)
    
    # Zaman Damgaları
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Settings {self.site_title}>'
        
    @staticmethod
    def get_settings():
        """Get site settings. If not exists, create default settings."""
        settings = Settings.query.first()
        if not settings:
            settings = Settings()
            db.session.add(settings)
            db.session.commit()
        return settings 