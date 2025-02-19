from datetime import datetime
from apps.extensions import db

class Widget(db.Model):
    __tablename__ = 'widgets'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # html, text, menu, vb.
    content = db.Column(db.Text)
    position = db.Column(db.String(50))  # sidebar, footer, header, vb.
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __str__(self):
        return self.title 