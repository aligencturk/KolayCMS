from app import create_app
from apps import db
from apps.models import SiteSettings

app = create_app()

with app.app_context():
    # Mevcut ayarları al
    settings = SiteSettings.query.first()
    
    if settings:
        # Navbar ayarlarını güncelle
        settings.navbar_bg_color = '#ffffff'
        settings.navbar_text_color = '#000000'
        settings.navbar_active_color = '#007bff'
        settings.navbar_hover_color = '#0056b3'
        settings.navbar_is_fixed = True
        settings.navbar_is_transparent = False
        settings.navbar_font_family = 'inherit'
        settings.navbar_font_size = '1rem'
        
        try:
            db.session.commit()
            print("Site ayarları başarıyla güncellendi.")
        except Exception as e:
            db.session.rollback()
            print(f"Hata oluştu: {str(e)}")
    else:
        print("Site ayarları bulunamadı.") 