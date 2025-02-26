import sqlite3

try:
    # Veritabanına bağlan
    conn = sqlite3.connect("instance/cms.db")
    cursor = conn.cursor()
    
    # Theme tablosunun sütunlarını listele
    cursor.execute("PRAGMA table_info(theme)")
    columns = cursor.fetchall()
    
    print("Theme tablosundaki sütunlar:")
    for column in columns:
        print(f"{column[1]} ({column[2]})")
    
    # Mevcut temaları listele
    print("\nMevcut temalar:")
    cursor.execute("SELECT id, name, is_active FROM theme")
    themes = cursor.fetchall()
    for theme in themes:
        print(f"ID: {theme[0]}, Adı: {theme[1]}, Aktif: {theme[2]}")
    
    # Bağlantıyı kapat
    conn.close()
except Exception as e:
    print(f"Hata: {e}") 