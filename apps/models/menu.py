from datetime import datetime
from apps import db

class Menu(db.Model):
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, db.ForeignKey('menus.id', ondelete='CASCADE', name='fk_menu_parent'))
    menu_type = db.Column(db.String(20), default='header')  # header, footer, sidebar
    icon = db.Column(db.String(50))  # FontAwesome icon class
    permission = db.Column(db.String(50))  # menu access permission
    css_class = db.Column(db.String(50))  # custom CSS class
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    parent = db.relationship('Menu', remote_side=[id], backref=db.backref('children', cascade='all, delete-orphan'), lazy='joined')
    
    def __str__(self):
        return self.title
        
    def __repr__(self):
        return f'<Menu {self.title}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'order': self.order,
            'parent_id': self.parent_id,
            'menu_type': self.menu_type,
            'icon': self.icon,
            'permission': self.permission,
            'css_class': self.css_class,
            'is_active': self.is_active
        } 