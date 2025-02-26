#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3

def check_table_schema(table_name):
    """Belirtilen tablonun şemasını kontrol eder"""
    print(f"{table_name} tablosunun şeması kontrol ediliyor...")
    
    # Veritabanı bağlantısı oluştur
    conn = sqlite3.connect('kolaycms.db')
    cursor = conn.cursor()
    
    try:
        # Tablo şemasını al
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\n{table_name} tablosunun sütunları:")
        for column in columns:
            print(f"  - {column[1]} ({column[2]})")
        
    except Exception as e:
        print(f"Hata oluştu: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_table_schema("blog_posts")
    check_table_schema("pages") 