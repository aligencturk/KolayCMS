import os
import shutil
from app import create_app
from apps import db
from apps.models import SiteSettings, User
from werkzeug.security import generate_password_hash

# Veritabanını yedekle
if os.path.exists('kolaycms.db'):
    shutil.copy2('kolaycms.db', 'kolaycms_backup_before_reset.db')
    print("Veritabanı yedeklendi.")

app = create_app()

with app.app_context():
    # Veritabanını sil ve yeniden oluştur
    db.drop_all()
    db.create_all()
    print("Veritabanı yeniden oluşturuldu.")
    
    # Admin kullanıcısı oluştur
    admin = User(
        username='admin',
        email='admin@kolaycms.com',
        role='admin',
        is_active=True
    )
    admin.set_password('admin123')
    db.session.add(admin)
    
    # Varsayılan site ayarlarını oluştur
    settings = SiteSettings(
        site_title='KolayCMS',
        site_description='Modern ve Kolay Yönetilebilir İçerik Yönetim Sistemi',
        meta_keywords='cms, içerik yönetim sistemi, web sitesi',
        
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
        print("Varsayılan veriler oluşturuldu.")
    except Exception as e:
        db.session.rollback()
        print(f"Hata oluştu: {str(e)}")
        
        # Hata durumunda yedekten geri yükle
        if os.path.exists('kolaycms_backup_before_reset.db'):
            os.remove('kolaycms.db')
            shutil.copy2('kolaycms_backup_before_reset.db', 'kolaycms.db')
            print("Veritabanı yedekten geri yüklendi.") 