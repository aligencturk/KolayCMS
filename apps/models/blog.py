from datetime import datetime
from . import db
from slugify import slugify

class BlogPost(db.Model):
    __tablename__ = 'blog_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False)
    content = db.Column(db.Text)
    excerpt = db.Column(db.Text)
    featured_image = db.Column(db.String(255))
    meta_title = db.Column(db.String(200))
    meta_description = db.Column(db.Text)
    is_published = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, onupdate=datetime.now)
    published_at = db.Column(db.DateTime)
    
    # İlişkiler
    author = db.relationship('User', backref='blog_posts')
    
    def __init__(self, *args, **kwargs):
        if not kwargs.get('slug') and kwargs.get('title'):
            kwargs['slug'] = slugify(kwargs['title'])
        super().__init__(*args, **kwargs)
    
    def __repr__(self):
        return f'<BlogPost {self.title}>' 