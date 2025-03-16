import os
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import json

# Firebase başlatma
cred_path = os.path.join(os.getcwd(), 'kolaycms-8c482-firebase-adminsdk-fbsvc-b881455bed.json')
if os.path.exists(cred_path):
    print(f"Servis hesabı dosyası bulundu: {cred_path}")
    
    # Firebase başlat
    cred = credentials.Certificate(cred_path)
    try:
        firebase_admin.initialize_app(cred)
    except ValueError:
        print("Firebase zaten başlatılmış, mevcut uygulama kullanılıyor...")
    
    # Firestore client
    db = firestore.client()
    print("Firebase başarıyla başlatıldı")
    
    # Cobsine temasını ekle
    theme_id = 'cobsine'
    theme_path = os.path.join(os.getcwd(), 'themes', theme_id)
    
    if os.path.exists(theme_path):
        print(f"Tema dizini bulundu: {theme_path}")
        
        # Tema bilgilerini hazırla
        now = datetime.datetime.now().isoformat()
        theme_data = {
            'name': 'Cobsine',
            'description': 'Modern ve şık bir tema',
            'is_active': False,
            'author': 'KolayCMS',
            'version': '1.0.0',
            'created_at': now,
            'updated_at': now,
            'directory': theme_path,
            'template_directory': os.path.join(theme_path, 'templates'),
            'css_directory': os.path.join(theme_path, 'static', 'css'),
            'js_directory': os.path.join(theme_path, 'static', 'js'),
            'img_directory': os.path.join(theme_path, 'static', 'images')
        }
        
        # Veritabanına ekle
        db.collection('themes').document(theme_id).set(theme_data)
        print(f"Tema başarıyla eklendi: {theme_id}")
    else:
        print(f"HATA: Tema dizini bulunamadı: {theme_path}")
else:
    print(f"HATA: Servis hesabı dosyası bulunamadı: {cred_path}") 