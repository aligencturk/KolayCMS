class SiteSettings(db.Model):
    __tablename__ = 'site_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    site_name = db.Column(db.String(100), nullable=False, default='KolayCMS')
    site_description = db.Column(db.Text)
    site_keywords = db.Column(db.String(255))
    site_author = db.Column(db.String(100))
    site_url = db.Column(db.String(255))
    admin_email = db.Column(db.String(100))
    google_analytics = db.Column(db.String(50))
    facebook_pixel = db.Column(db.String(50))
    maintenance_mode = db.Column(db.Boolean, default=False)
    active_theme = db.Column(db.String(50), default='default')
    theme_settings = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SiteSettings {self.site_name}>' 