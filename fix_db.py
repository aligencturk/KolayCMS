from app import create_app
from apps import db
from apps.models import SiteSettings

app = create_app()

with app.app_context():
    # Veritabanını sil ve yeniden oluştur
    db.drop_all()
    db.create_all()
    print("Veritabanı yeniden oluşturuldu.")
    
    # Basit bir site ayarı oluştur
    settings = SiteSettings()
    settings.site_title = 'KolayCMS'
    settings.site_description = 'Modern ve Kolay Yönetilebilir İçerik Yönetim Sistemi'
    settings.primary_color = '#007bff'
    settings.secondary_color = '#6c757d'
    settings.navbar_bg_color = '#ffffff'
    settings.navbar_text_color = '#000000'
    settings.navbar_active_color = '#007bff'
    settings.navbar_hover_color = '#0056b3'
    settings.navbar_is_fixed = True
    settings.navbar_is_transparent = False
    settings.navbar_font_family = 'inherit'
    settings.navbar_font_size = '1rem'
    
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
        print(f"Settings özellikleri: {dir(settings)}") 