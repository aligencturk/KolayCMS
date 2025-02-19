from app import create_app
from apps.models import db, Slide, SiteSettings
import os
from sqlalchemy import text

app = create_app()

with app.app_context():
    # Veritabanını ve tabloları oluştur
    db.create_all()
    
    # Değişiklikleri kaydet
    db.session.commit()
    
    print("Veritabanı başarıyla oluşturuldu!")

    # Tüm tabloları kontrol et
    result = db.session.execute(text("""
        SELECT 
            name AS TableName
        FROM sqlite_master 
        WHERE type='table'
        ORDER BY name;
    """))
    
    print("\nTablo Listesi:")
    print("=" * 80)
    for row in result:
        table_name = row.TableName
        print(f"\nTablo: {table_name}")
        
        # Her tablonun yapısını kontrol et
        columns = db.session.execute(text(f"PRAGMA table_info('{table_name}')"))
        for col in columns:
            print(f"  Kolon: {col.name}")
            print(f"  Tip: {col.type}")
            print(f"  Null?: {'Hayır' if col.notnull else 'Evet'}")
            print(f"  Primary Key?: {'Evet' if col.pk else 'Hayır'}")
            print("-" * 40)
    
    # Admin kullanıcı sayısını kontrol et
    result = db.session.execute(text("""
        SELECT COUNT(*) as count 
        FROM users 
        WHERE role = 'admin'
    """))
    
    print("\nAdmin Sayısı:")
    print("=" * 80)
    for row in result:
        print(f"Admin Sayısı: {row.count}")
        print("-" * 80)

    # Tüm slaytları listele
    slides = Slide.query.all()
    print("\nMevcut Slaytlar:")
    for slide in slides:
        print(f"ID: {slide.id}")
        print(f"Başlık: {slide.title}")
        print(f"Açıklama: {slide.description}")
        print(f"Görsel: {slide.image}")
        print(f"Aktif: {slide.is_active}")
        print("-" * 50)
    
    # Eğer hiç slayt yoksa, varsayılan slaytları ekle
    if not slides:
        print("\nHiç slayt bulunamadı. Varsayılan slaytlar ekleniyor...")
        default_slides = [
            {
                'title': 'Business Agency Profit Your Marketing',
                'description': 'It is a long established fact that a reader will be distracted by the readable content of a page when',
                'button_text': 'Contact Us',
                'button_url': '/contact',
                'order': 1,
                'is_active': True,
                'image_path': '/static/cobsin_template/images/banner-bg.png'
            },
            {
                'title': 'Grow Your Business With Us',
                'description': 'We help businesses achieve their goals through innovative solutions and strategic planning',
                'button_text': 'Read More',
                'button_url': '/about',
                'order': 2,
                'is_active': True,
                'image_path': '/static/cobsin_template/images/banner-bg.png'
            }
        ]
        
        for slide_data in default_slides:
            slide = Slide(**slide_data)
            db.session.add(slide)
        
        try:
            db.session.commit()
            print("Varsayılan slaytlar başarıyla eklendi.")
        except Exception as e:
            db.session.rollback()
            print(f"Hata: {str(e)}")

    # Get the first site settings record
    settings = SiteSettings.query.first()
    
    if settings:
        # Get all columns
        columns = SiteSettings.__table__.columns
        print("\nMevcut sütunlar:")
        for column in columns:
            print(f"Sütun: {column.name}, Tip: {column.type}, Nullable: {column.nullable}")
            
        print("\nMevcut değerler:")
        for column in columns:
            value = getattr(settings, column.name)
            print(f"{column.name}: {value}")
    else:
        print("Hiç site ayarı bulunamadı") 