import sqlite3

# Veritabanına bağlan
conn = sqlite3.connect('instance/cms.db')
cursor = conn.cursor()

# Tüm tabloları listele
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Veritabanındaki tablolar:")
for table in tables:
    print(f"- {table[0]}")

# SiteSettings tablosunu kontrol et
if ('site_settings',) in tables:
    cursor.execute('PRAGMA table_info(site_settings)')
    columns = cursor.fetchall()
    print("\nsite_settings tablosundaki sütunlar:")
    for col in columns:
        print(f"- {col[1]} ({col[2]})")

# Bağlantıyı kapat
conn.close() 