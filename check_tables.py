import sqlite3

# Veritabanına bağlan
conn = sqlite3.connect('instance/kolaycms.db')
cursor = conn.cursor()

# Tüm tabloları listele
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Veritabanındaki tablolar:")
for table in tables:
    print(f"- {table[0]}")

# Bağlantıyı kapat
conn.close() 