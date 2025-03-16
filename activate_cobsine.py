import os
import sys
import json
from datetime import datetime

"""
CoBsine temasını etkinleştirmek için basit script
"""

def main():
    # Tema adı 
    theme_name = "CoBsine"
    
    # Mevcut dizini ve tema klasörünü kontrol et
    cwd = os.getcwd()
    theme_path = os.path.join(cwd, "themes", theme_name)
    if not os.path.exists(theme_path):
        theme_path = os.path.join(cwd, "themes", theme_name.lower())
        if not os.path.exists(theme_path):
            print(f"Hata: {theme_name} teması bulunamadı")
            sys.exit(1)
    
    # Tema şablonlarını ve statik dosyaları kontrol et
    templates_path = os.path.join(theme_path, "templates")
    static_path = os.path.join(theme_path, "static")
    
    if not os.path.exists(templates_path) or not os.path.exists(static_path):
        print(f"Hata: Tema dosyaları eksik veya yapısı hatalı")
        sys.exit(1)
    
    # Tema.json dosyasını kontrol et ve oluştur
    theme_json_path = os.path.join(theme_path, "theme.json")
    if not os.path.exists(theme_json_path):
        print(f"Tema JSON dosyası bulunamadı, yeni oluşturuluyor...")
        theme_data = {
            "name": theme_name,
            "version": "1.0.0",
            "description": "Modern, çok amaçlı kurumsal web sitesi teması",
            "author": "CoBsine",
            "thumbnail_url": "",
            "colors": {
                "primary": "#1f1f1f",
                "secondary": "#4aafff"
            },
            "fonts": {
                "primary": "Poppins, sans-serif",
                "secondary": "Roboto, sans-serif"
            }
        }
        
        with open(theme_json_path, 'w', encoding='utf-8') as f:
            json.dump(theme_data, f, indent=2)
    
    print(f"✅ {theme_name} teması kontrol edildi ve hazır.")
    print(f"⚠️ Önemli: Aşağıdaki işlemleri yapın:")
    print(f"  1. Web arayüzünden Tema Yönetimi sayfasına gidin")
    print(f"  2. Tema listesindeki '{theme_name}' temasını bulun")
    print(f"  3. 'Aktifleştir' butonuna tıklayın")
    print(f"  4. Ardından http://localhost:5000/themes/website/{theme_name} adresini ziyaret edin")

if __name__ == "__main__":
    main() 