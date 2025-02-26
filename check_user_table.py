import sqlite3

try:
    # Veritabanına bağlan
    conn = sqlite3.connect("instance/cms.db")
    cursor = conn.cursor()
    
    # User tablosunun sütunlarını listele
    cursor.execute("PRAGMA table_info(user)")
    columns = cursor.fetchall()
    
    print("User tablosundaki sütunlar:")
    for column in columns:
        print(f"{column[1]} ({column[2]})")
    
    # Bağlantıyı kapat
    conn.close()
except Exception as e:
    print(f"Hata: {e}") 