from app import create_app
from apps import db
from apps.models import SiteSettings

app = create_app()

with app.app_context():
    # Mevcut ayarları kontrol et
    settings = SiteSettings.query.first()
    
    if not settings:
        # Varsayılan ayarları oluştur
        settings = SiteSettings(
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
            
            # Footer Ayarları
            footer_bg_color='#343a40',
            footer_text_color='#ffffff',
            footer_link_color='#ffffff',
            footer_font_family='inherit',
            footer_font_size='1rem',
            footer_about='KolayCMS ile web sitenizi kolayca yönetin.'
        )
        
        db.session.add(settings)
        db.session.commit()
        print("Varsayılan site ayarları oluşturuldu.")
    else:
        print("Site ayarları zaten mevcut.") 