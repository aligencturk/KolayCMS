import sqlite3

# Veritabanına bağlan
conn = sqlite3.connect('instance/kolaycms.db')
cursor = conn.cursor()

# active_theme sütununu kontrol et
cursor.execute('PRAGMA table_info(site_settings)')
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

# Eğer active_theme sütunu yoksa ekle
if 'active_theme' not in column_names:
    cursor.execute("ALTER TABLE site_settings ADD COLUMN active_theme TEXT DEFAULT 'default'")
    print("active_theme sütunu eklendi")
else:
    print("active_theme sütunu zaten var")

# Değişiklikleri kaydet ve bağlantıyı kapat
conn.commit()
conn.close() 