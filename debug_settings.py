from app import create_app
from apps import db
from apps.models import SiteSettings

app = create_app()

with app.app_context():
    # Mevcut ayarları al
    settings = SiteSettings.query.first()
    
    if settings:
        print("\nSettings Nesne Bilgileri:")
        print(f"Tip: {type(settings)}")
        print(f"Sınıf: {settings.__class__}")
        print(f"Tablename: {settings.__class__.__tablename__}")
        
        print("\nMevcut Öznitelikler:")
        for attr in dir(settings):
            if not attr.startswith('_'):  # Özel metodları atla
                try:
                    value = getattr(settings, attr)
                    if not callable(value):  # Metodları atla
                        print(f"{attr}: {value}")
                except Exception as e:
                    print(f"{attr}: HATA - {str(e)}")
        
        print("\nVeritabanı Sütunları:")
        for column in settings.__table__.columns:
            print(f"Sütun: {column.name}, Tip: {column.type}, Varsayılan: {column.default}")
            
        # SQLAlchemy metadata'yı kontrol et
        print("\nSQLAlchemy Metadata:")
        for key in settings.__mapper__.attrs.keys():
            print(f"Attr: {key}")
            
        # Doğrudan veritabanından kontrol et
        result = db.session.execute(db.text("SELECT * FROM site_settings LIMIT 1")).fetchone()
        if result:
            print("\nVeritabanından Ham Veri:")
            for key in result.keys():
                print(f"{key}: {result[key]}")
    else:
        print("Site ayarları bulunamadı.") 