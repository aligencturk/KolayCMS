from app import create_app
from apps import db
from migrations.add_navbar_settings import upgrade

app = create_app()

with app.app_context():
    # Veritabanı yedeklemesi
    with open('kolaycms.db', 'rb') as source:
        with open('kolaycms_backup_before_navbar.db', 'wb') as target:
            target.write(source.read())
    
    print("Veritabanı yedeklendi.")
    
    try:
        # Migration'ı çalıştır
        upgrade()
        print("Navbar ayarları başarıyla eklendi.")
    except Exception as e:
        print(f"Hata oluştu: {str(e)}")
        print("Yedeklenen veritabanını geri yüklüyorum...")
        
        # Hata durumunda yedekten geri yükle
        with open('kolaycms_backup_before_navbar.db', 'rb') as source:
            with open('kolaycms.db', 'wb') as target:
                target.write(source.read())
        
        print("Veritabanı yedekten geri yüklendi.") 