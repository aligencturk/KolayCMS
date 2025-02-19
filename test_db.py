import pyodbc

conn_str = (
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=localhost\\SQLEXPRESS;'
    'DATABASE=FlaskCMS;'
    'Trusted_Connection=yes;'
    'TrustServerCertificate=yes;'
)

try:
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    print("Veritabanına başarıyla bağlandı!")
    
    # Veritabanı tablolarını listele
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE'")
    tables = cursor.fetchall()
    print("\nMevcut tablolar:")
    for table in tables:
        print(f"- {table[0]}")
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Bağlantı hatası: {str(e)}") 