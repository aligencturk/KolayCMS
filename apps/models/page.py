from datetime import datetime
from apps.extensions import db
from apps.models.content_types import ContactInfo

class Page(db.Model):
    __tablename__ = 'pages'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text, nullable=True)
    template = db.Column(db.String(50), default='default')  # Şablon tipi: default, full-width, sidebar, landing
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # İlişkiler
    contact_info = db.relationship('ContactInfo', backref='page', uselist=False, cascade='all, delete-orphan')
    
    def __str__(self):
        return self.title
    
    def __repr__(self):
        return f'<Page {self.title}>' 