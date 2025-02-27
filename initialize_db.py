from apps import create_app, db
from apps.models import User
from werkzeug.security import generate_password_hash
import os

def init_db():
    app = create_app()
    with app.app_context():
        # Veritabanı tabloları oluştur
        db.create_all()
        
        # Admin kullanıcısı ekle (eğer yoksa)
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                email='admin@example.com',
                role='admin',
                is_active=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin kullanıcısı oluşturuldu!")
        else:
            print("Admin kullanıcısı zaten var.")
            
if __name__ == '__main__':
    init_db() 