import sqlite3

try:
    # Veritabanına bağlan
    conn = sqlite3.connect("instance/cms.db")
    cursor = conn.cursor()
    
    # Tabloları listele
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("Mevcut tablolar:")
    for table in tables:
        print(table[0])
    
    # Bağlantıyı kapat
    conn.close()
except Exception as e:
    print(f"Hata: {e}") 