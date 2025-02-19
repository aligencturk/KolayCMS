from datetime import datetime
from apps.extensions import db

class Theme(db.Model):
    __tablename__ = 'themes'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    folder_name = db.Column(db.String(100), unique=True, nullable=False)
    version = db.Column(db.String(20))
    author = db.Column(db.String(100))
    screenshot_url = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=False)
    settings = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __str__(self):
        return self.name 