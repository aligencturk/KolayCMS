from datetime import datetime
from apps.extensions import db

class Content(db.Model):
    __tablename__ = 'contents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=True)
    content_type = db.Column(db.String(50), nullable=False, default='text')
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id'), nullable=True)
    position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    # İlişkiler
    page = db.relationship('Page', backref=db.backref('contents', lazy=True))
    
    def __str__(self):
        return self.title
    
    def __repr__(self):
        return f'<Content {self.title}>' 