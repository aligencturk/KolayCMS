import os
from app import create_app, db
from apps.models import User

def reset_database():
    app = create_app()
    
    with app.app_context():
        # Veritabanı dosyasını sil
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kolaycms.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print("Veritabanı silindi.")
        
        # Tabloları yeniden oluştur
        db.create_all()
        print("Tablolar oluşturuldu.")
        
        # Admin kullanıcısını oluştur
        admin = User(
            username='admin',
            email='admin@kolaycms.com',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin kullanıcısı oluşturuldu.")

if __name__ == '__main__':
    reset_database() 