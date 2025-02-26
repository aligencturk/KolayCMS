#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import os

def add_indexes(conn):
    cursor = conn.cursor()
    try:
        print("Pages tablosuna indeksler ekleniyor...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pages_slug ON pages(slug)")
        print("idx_pages_slug indeksi eklendi")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pages_title_is_published ON pages(title, is_published)")
        print("idx_pages_title_is_published indeksi eklendi")
        
        print("\nBlogPost tablosuna indeksler ekleniyor...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_blog_posts_title ON blog_posts(title)")
        print("idx_blog_posts_title indeksi eklendi")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_blog_posts_slug ON blog_posts(slug)")
        print("idx_blog_posts_slug indeksi eklendi")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_blog_posts_created_at ON blog_posts(created_at)")
        print("idx_blog_posts_created_at indeksi eklendi")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_blog_posts_title_is_active ON blog_posts(title, is_active)")
        print("idx_blog_posts_title_is_active indeksi eklendi")
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Hata oluştu: {e}")
        raise

def optimize_database(db_path):
    print("\nVeritabanı optimize ediliyor...")
    try:
        # VACUUM için ayrı bir bağlantı açıyoruz
        vacuum_conn = sqlite3.connect(db_path)
        vacuum_conn.isolation_level = None  # Otomatik commit modunu etkinleştir
        vacuum_conn.execute("VACUUM")
        print("VACUUM işlemi tamamlandı")
        vacuum_conn.close()
        
        # ANALYZE için yeni bir bağlantı
        analyze_conn = sqlite3.connect(db_path)
        analyze_conn.execute("ANALYZE")
        print("ANALYZE işlemi tamamlandı")
        analyze_conn.close()
        
        print("Veritabanı optimizasyonu başarıyla tamamlandı")
    except Exception as e:
        print(f"Optimizasyon sırasında hata oluştu: {e}")

if __name__ == "__main__":
    db_path = "kolaycms.db"
    
    try:
        print("Veritabanı şeması güncelleniyor...")
        conn = sqlite3.connect(db_path)
        
        # Alembic version tablosunu kontrol et ve güncelle
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='alembic_version'")
        if cursor.fetchone():
            cursor.execute("DELETE FROM alembic_version")
            print("Alembic version tablosu temizlendi")
        else:
            cursor.execute("CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL)")
            
        cursor.execute("INSERT INTO alembic_version (version_num) VALUES ('1')")
        print("Alembic version tablosu oluşturuldu ve sürüm '1' olarak ayarlandı")
        conn.commit()
        
        # İndeksleri ekle
        add_indexes(conn)
        
        # Bağlantıyı kapat
        conn.close()
        
        # Veritabanını optimize et (ayrı bir bağlantıda)
        optimize_database(db_path)
        
        print("Veritabanı şema güncellemesi başarıyla tamamlandı")
    except Exception as e:
        print(f"Şema güncellemesi sırasında hata oluştu: {e}") 