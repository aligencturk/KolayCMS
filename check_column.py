import sqlite3

def check_table_columns(db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute(f'PRAGMA table_info({table_name})')
    columns = cursor.fetchall()
    
    print(f"\nColumns in {table_name} table:")
    for col in columns:
        print(f"Column: {col[1]}, Type: {col[2]}, Nullable: {col[3]}, Default: {col[4]}")
    
    conn.close()

if __name__ == "__main__":
    check_table_columns('kolaycms.db', 'site_settings') 