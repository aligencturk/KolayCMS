from datetime import datetime
from apps.extensions import db

class Menu(db.Model):
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200))
    position = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, db.ForeignKey('menus.id'))
    is_mega_menu = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # İlişkiler
    parent = db.relationship('Menu', remote_side=[id], backref=db.backref('children', lazy='dynamic'))
    
    def __str__(self):
        return self.name 