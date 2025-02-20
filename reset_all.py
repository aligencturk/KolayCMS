import os
import shutil
from app import create_app
from apps import db
from apps.models import User, SiteSettings

def reset_database():
    # Veritabanını yedekle
    if os.path.exists('kolaycms.db'):
        shutil.copy2('kolaycms.db', 'kolaycms_backup_final.db')
        print("Veritabanı yedeklendi.")
        os.remove('kolaycms.db')
        print("Eski veritabanı silindi.")

    app = create_app()

    with app.app_context():
        # Yeni veritabanını oluştur
        db.create_all()
        print("Yeni veritabanı oluşturuldu.")
        
        # Admin kullanıcısı oluştur
        admin = User(
            username='admin',
            email='admin@kolaycms.com',
            role='admin',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        print("Admin kullanıcısı oluşturuldu.")
        
        # Site ayarlarını oluştur
        settings = SiteSettings(
            # Genel Ayarlar
            site_title='KolayCMS',
            site_description='Modern ve Kolay Yönetilebilir İçerik Yönetim Sistemi',
            
            # Tema Ayarları
            primary_color='#007bff',
            secondary_color='#6c757d',
            
            # Navbar Ayarları
            navbar_bg_color='#ffffff',
            navbar_text_color='#000000',
            navbar_active_color='#007bff',
            navbar_hover_color='#0056b3',
            navbar_is_fixed=True,
            navbar_is_transparent=False,
            navbar_font_family='inherit',
            navbar_font_size='1rem',
            
            # Body Ayarları
            body_bg_color='#ffffff',
            body_text_color='#212529',
            body_link_color='#007bff',
            body_font_family='Poppins, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            body_font_size='14px',
            body_line_height='1.5',
            
            # Footer Ayarları
            footer_bg_color='#343a40',
            footer_text_color='#ffffff',
            footer_link_color='#ffffff',
            footer_font_family='inherit',
            footer_font_size='1rem',
            footer_about='KolayCMS ile web sitenizi kolayca yönetin.'
        )
        
        db.session.add(settings)
        
        try:
            db.session.commit()
            print("Site ayarları oluşturuldu.")
        except Exception as e:
            db.session.rollback()
            print(f"Hata: {str(e)}")
            
            # Hata detaylarını göster
            print("\nHata Detayları:")
            print(f"Settings sınıfı: {type(settings)}")
            print(f"Settings sütunları: {[c.name for c in settings.__table__.columns]}")
            
            # Yedekten geri yükle
            if os.path.exists('kolaycms_backup_final.db'):
                if os.path.exists('kolaycms.db'):
                    os.remove('kolaycms.db')
                shutil.copy2('kolaycms_backup_final.db', 'kolaycms.db')
                print("Veritabanı yedekten geri yüklendi.")

if __name__ == "__main__":
    reset_database() 