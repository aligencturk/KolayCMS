from datetime import datetime
from apps.extensions import db
from slugify import slugify

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    image_path = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # İlişkiler
    parent = db.relationship('Category', remote_side=[id], backref=db.backref('children', lazy='dynamic'))
    
    def __str__(self):
        return self.name
    
    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)
        db.session.add(self)
        db.session.commit()

class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    image_path = db.Column(db.String(200))
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    sku = db.Column(db.String(50), unique=True)
    weight = db.Column(db.Float)
    dimensions = db.Column(db.String(50))
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # İlişkiler
    category = db.relationship('Category', backref=db.backref('products', lazy='dynamic'), lazy='joined')
    
    def __str__(self):
        return self.name
    
    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.sku:
            self.sku = f"PRD-{datetime.now().strftime('%Y%m%d')}-{self.id}"
        db.session.add(self)
        db.session.commit() 