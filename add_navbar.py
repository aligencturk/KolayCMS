import sqlite3
import shutil
import os

# Veritabanını yedekle
shutil.copy2('kolaycms.db', 'kolaycms_backup_before_navbar.db')
print("Veritabanı yedeklendi.")

try:
    # Veritabanına bağlan
    conn = sqlite3.connect('kolaycms.db')
    cursor = conn.cursor()
    
    # Yeni sütunları ekle
    alter_commands = [
        "ALTER TABLE site_settings ADD COLUMN navbar_bg_color VARCHAR(10) NOT NULL DEFAULT '#ffffff'",
        "ALTER TABLE site_settings ADD COLUMN navbar_text_color VARCHAR(10) NOT NULL DEFAULT '#000000'",
        "ALTER TABLE site_settings ADD COLUMN navbar_active_color VARCHAR(10) NOT NULL DEFAULT '#007bff'",
        "ALTER TABLE site_settings ADD COLUMN navbar_hover_color VARCHAR(10) NOT NULL DEFAULT '#0056b3'",
        "ALTER TABLE site_settings ADD COLUMN navbar_is_fixed BOOLEAN NOT NULL DEFAULT 1",
        "ALTER TABLE site_settings ADD COLUMN navbar_is_transparent BOOLEAN NOT NULL DEFAULT 0",
        "ALTER TABLE site_settings ADD COLUMN navbar_font_family VARCHAR(50) DEFAULT 'inherit'",
        "ALTER TABLE site_settings ADD COLUMN navbar_font_size VARCHAR(10) DEFAULT '1rem'"
    ]
    
    for command in alter_commands:
        try:
            cursor.execute(command)
            print(f"Komut başarıyla çalıştırıldı: {command}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"Sütun zaten mevcut, atlanıyor: {command}")
            else:
                raise e
    
    # Değişiklikleri kaydet
    conn.commit()
    print("Tüm navbar ayarları başarıyla eklendi.")

except Exception as e:
    print(f"Hata oluştu: {str(e)}")
    print("Yedeklenen veritabanını geri yüklüyorum...")
    
    # Bağlantıyı kapat
    conn.close()
    
    # Hata durumunda yedekten geri yükle
    os.remove('kolaycms.db')
    shutil.copy2('kolaycms_backup_before_navbar.db', 'kolaycms.db')
    print("Veritabanı yedekten geri yüklendi.")
    
else:
    # Bağlantıyı kapat
    conn.close() 