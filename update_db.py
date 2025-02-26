from app import create_app
from apps.extensions import db
from sqlalchemy import text

# Flask uygulamasını oluştur ve uygulama bağlamını başlat
app = create_app()
with app.app_context():
    try:
        # active_theme sütununu ekle
        db.session.execute(text('ALTER TABLE site_settings ADD COLUMN active_theme VARCHAR(50) DEFAULT "default"'))
        print("active_theme sütunu eklendi")
    except Exception as e:
        print(f"active_theme sütunu eklenirken hata: {str(e)}")
    
    try:
        # theme_settings sütununu ekle
        db.session.execute(text('ALTER TABLE site_settings ADD COLUMN theme_settings JSON'))
        print("theme_settings sütunu eklendi")
    except Exception as e:
        print(f"theme_settings sütunu eklenirken hata: {str(e)}")
    
    # Değişiklikleri kaydet
    db.session.commit()
    print("Veritabanı şeması güncellendi.") 