from datetime import datetime
from apps import db

class Menu(db.Model):
    __tablename__ = 'menus'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, db.ForeignKey('menus.id', ondelete='CASCADE'))
    menu_type = db.Column(db.String(20), default='header')  # header, footer, sidebar
    icon = db.Column(db.String(50), nullable=True)  # FontAwesome icon class
    permission = db.Column(db.String(50), nullable=True)  # menu access permission
    css_class = db.Column(db.String(50), nullable=True)  # custom CSS class
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    parent = db.relationship(
        'Menu',
        remote_side=[id],
        backref=db.backref('children', lazy='joined'),
        lazy='joined'
    )
    
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
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class MenuItem(db.Model):
    __tablename__ = 'menu_items'
    
    id = db.Column(db.Integer, primary_key=True)
    menu_id = db.Column(db.Integer, db.ForeignKey('menus.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    order = db.Column(db.Integer, default=0)
    parent_id = db.Column(db.Integer, db.ForeignKey('menu_items.id', ondelete='CASCADE'))
    target = db.Column(db.String(10), default='_self')  # _self, _blank, _parent, _top
    icon = db.Column(db.String(50), nullable=True)  # FontAwesome icon class
    css_class = db.Column(db.String(50), nullable=True)  # custom CSS class
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # İlişkiler
    menu = db.relationship('Menu', backref='items')
    parent = db.relationship(
        'MenuItem',
        remote_side=[id],
        backref=db.backref('children', lazy='joined'),
        lazy='joined'
    )
    
    def __str__(self):
        return self.title
        
    def __repr__(self):
        return f'<MenuItem {self.title}>'
        
    def to_dict(self):
        return {
            'id': self.id,
            'menu_id': self.menu_id,
            'title': self.title,
            'url': self.url,
            'order': self.order,
            'parent_id': self.parent_id,
            'target': self.target,
            'icon': self.icon,
            'css_class': self.css_class,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 