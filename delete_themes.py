from google.cloud import firestore
import os
import shutil
from firebase_admin import credentials, initialize_app, firestore
import firebase_admin

# Firebase başlatma
try:
    # Eğer zaten başlatılmışsa hata verecek, onu yakalayalım
    firebase_admin.get_app()
except ValueError:
    # Servis hesabı anahtarı
    cred = credentials.Certificate("firebase-credentials.json")
    initialize_app(cred)

print("Firebase bağlantısı kuruldu.")

# Firestore bağlantısı
db = firestore.client()

# Tüm temaları al
themes_ref = db.collection('themes')
themes = list(themes_ref.stream())

print(f"Toplam {len(themes)} tema bulundu.")

# Temaları sil
for theme in themes:
    theme_id = theme.id
    theme_data = theme.to_dict()
    print(f"Tema siliniyor: {theme_id} - {theme_data.get('name', 'Bilinmeyen Tema')}")
    
    # Firestore'dan sil
    themes_ref.document(theme_id).delete()
    
    # Tema klasörünü sil (varsa)
    theme_dir = os.path.join('themes', theme_id)
    if os.path.exists(theme_dir):
        try:
            shutil.rmtree(theme_dir)
            print(f"  Tema dizini silindi: {theme_dir}")
        except Exception as e:
            print(f"  Tema dizini silinirken hata: {str(e)}")

print("Tüm temalar silindi.") 