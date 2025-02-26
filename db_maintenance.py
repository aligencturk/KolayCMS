import os
import shutil
from datetime import datetime
from app import create_app
from apps import db

app = create_app()

def optimize_database():
    """Veritabanını optimize eder (VACUUM ve ANALYZE işlemleri)"""
    with app.app_context():
        print("Veritabanı optimizasyonu başlatılıyor...")
        db.engine.execute('VACUUM;')  # Boş alanları temizler
        db.engine.execute('ANALYZE;')  # İstatistikleri günceller
        print("Veritabanı optimize edildi.")

def backup_database():
    """Veritabanının yedeğini alır"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = "backups"
    backup_path = f"{backup_dir}/kolaycms_{timestamp}.db"
    
    # Yedekleme klasörünü oluştur
    os.makedirs(backup_dir, exist_ok=True)
    
    # Veritabanını kopyala
    if os.path.exists("kolaycms.db"):
        shutil.copy2("kolaycms.db", backup_path)
        print(f"Veritabanı yedeklendi: {backup_path}")
    else:
        print("Veritabanı dosyası bulunamadı!")

def chunks(lst, n):
    """Listeyi n büyüklüğünde parçalara böler"""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

def bulk_import_data(model_class, items):
    """Verileri toplu olarak içe aktarır"""
    with app.app_context():
        try:
            total = len(items)
            chunk_size = 100
            processed = 0
            
            print(f"Toplam {total} kayıt içe aktarılıyor...")
            
            for chunk in chunks(items, chunk_size):
                db.session.bulk_insert_mappings(model_class, chunk)
                db.session.commit()
                
                processed += len(chunk)
                print(f"İlerleme: {processed}/{total} ({processed/total*100:.1f}%)")
                
            print("Veri aktarımı tamamlandı.")
        except Exception as e:
            db.session.rollback()
            print(f"Hata: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Kullanım: python db_maintenance.py [optimize|backup]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "optimize":
        optimize_database()
    elif command == "backup":
        backup_database()
    else:
        print(f"Bilinmeyen komut: {command}")
        print("Kullanım: python db_maintenance.py [optimize|backup]") 