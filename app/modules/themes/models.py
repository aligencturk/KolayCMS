from app import db, logger
from datetime import datetime
import os
import json
import zipfile
import rarfile
import shutil
import tempfile
from werkzeug.utils import secure_filename
from google.cloud import firestore
from flask import current_app

# WinRAR yolunu otomatik tespit et
def find_unrar():
    possible_paths = [
        r"C:\Program Files\WinRAR\UnRAR.exe",
        r"C:\Program Files (x86)\WinRAR\UnRAR.exe",
        os.path.join(os.environ.get('ProgramFiles', ''), 'WinRAR', 'UnRAR.exe'),
        os.path.join(os.environ.get('ProgramFiles(x86)', ''), 'WinRAR', 'UnRAR.exe')
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

# UnRAR.exe yolunu ayarla
unrar_path = find_unrar()
if unrar_path:
    rarfile.UNRAR_TOOL = unrar_path
    logger.info(f"UnRAR.exe bulundu: {unrar_path}")
else:
    logger.warning("UnRAR.exe bulunamadı! RAR dosyaları açılamayabilir.")

class Theme:
    """Tema modeli"""
    def __init__(self, id=None, name=None, description=None, version=None, 
                 author=None, preview_image=None, is_active=False, 
                 created_at=None, updated_at=None, template_dir=None, static_dir=None):
        self.id = id
        self.name = name
        self.description = description
        self.version = version
        self.author = author
        self.preview_image = preview_image
        self.is_active = is_active
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.template_dir = template_dir
        self.static_dir = static_dir
        
        # Eğer template_dir belirtilmemişse, otomatik oluştur
        if not self.template_dir and self.name:
            self.template_dir = os.path.join('themes', self.name.lower(), 'templates')
            
        # Eğer static_dir belirtilmemişse, otomatik oluştur
        if not self.static_dir and self.name:
            self.static_dir = os.path.join('themes', self.name.lower(), 'static')
    
    @staticmethod
    def from_dict(data, id=None):
        """Sözlükten tema nesnesi oluştur"""
        if not data:
            return None
            
        # Eğer data içinde 'id' varsa ve id parametresi de belirtilmişse, veri kopyasını oluşturup 'id' alanını kaldır
        if id is not None and 'id' in data:
            data_copy = data.copy()
            data_copy.pop('id', None)
            data = data_copy
            
        theme = Theme(
            id=id,
            name=data.get('name'),
            description=data.get('description'),
            version=data.get('version'),
            author=data.get('author'),
            preview_image=data.get('preview_image'),
            is_active=data.get('is_active', False),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            template_dir=data.get('template_dir'),
            static_dir=data.get('static_dir')
        )
        return theme
    
    def to_dict(self):
        """Tema verilerini sözlük olarak döndür"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'version': self.version,
            'author': self.author,
            'preview_image': self.preview_image,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'template_dir': self.template_dir,
            'static_dir': self.static_dir
        }

class ThemeModule:
    """Tema modülü"""
    def __init__(self):
        self.themes_dir = current_app.config.get('THEMES_FOLDER', os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'themes'))
        os.makedirs(self.themes_dir, exist_ok=True)
    
    async def get_all_themes(self):
        """Tüm temaları getir"""
        try:
            logger.debug("Tüm temalar getiriliyor...")
            themes_ref = db.collection('themes').stream()
            themes = []
            
            # Tema sayısını debug olarak yazdır
            theme_count = 0
            for _ in db.collection('themes').stream():
                theme_count += 1
            
            logger.debug(f"Veritabanında {theme_count} tema bulundu.")
            
            if theme_count == 0:
                logger.warning("Veritabanında hiç tema bulunamadı!")
            
            for doc in themes_ref:
                theme_data = doc.to_dict()
                theme_data['id'] = doc.id
                themes.append(theme_data)
                logger.debug(f"Tema verileri alındı: {doc.id} - {theme_data.get('name', 'İsimsiz')}")
                logger.debug(f"Tema aktiflik durumu: {theme_data.get('is_active', False)}")
                
            logger.debug(f"Toplam {len(themes)} tema verileri alındı.")
            return themes
        except Exception as e:
            logger.error(f"Temaları getirme hatası: {str(e)}", exc_info=True)
            return []
    
    async def get_theme(self, theme_id):
        """Belirli bir temayı getir"""
        try:
            theme_ref = db.collection('themes').document(theme_id).get()
            if theme_ref.exists:
                theme_data = theme_ref.to_dict()
                theme_data['id'] = theme_ref.id
                return theme_data
            return None
        except Exception as e:
            logger.error(f"Tema getirme hatası: {str(e)}", exc_info=True)
            return None
    
    async def get_active_theme(self):
        """Aktif temayı getir"""
        try:
            themes_ref = db.collection('themes').where('is_active', '==', True).limit(1).stream()
            for doc in themes_ref:
                theme_data = doc.to_dict()
                theme_data['id'] = doc.id
                return theme_data
            return None
        except Exception as e:
            logger.error(f"Aktif tema getirme hatası: {str(e)}", exc_info=True)
            return None
    
    async def activate_theme(self, theme_id):
        """Temayı aktifleştir"""
        try:
            logger.debug(f"Tema aktifleştiriliyor: {theme_id}")
            
            # Tema var mı kontrol et
            theme_doc = db.collection('themes').document(theme_id).get()
            if not theme_doc.exists:
                logger.error(f"Aktifleştirilecek tema bulunamadı: {theme_id}")
                return False
                
            # Aktif temanın bilgilerini al
            theme_data = theme_doc.to_dict()
            logger.debug(f"Aktifleştirilecek tema bulundu: {theme_data.get('name', 'İsimsiz')}")
            
            # Önce tüm temaları pasifleştir
            logger.debug("Tüm temalar pasifleştiriliyor...")
            themes_ref = db.collection('themes').stream()
            for doc in themes_ref:
                if doc.id != theme_id and doc.to_dict().get('is_active'):
                    logger.debug(f"Tema pasifleştiriliyor: {doc.id} - {doc.to_dict().get('name', 'İsimsiz')}")
                    db.collection('themes').document(doc.id).update({'is_active': False})
            
            # Seçilen temayı aktifleştir
            logger.debug(f"Tema aktifleştiriliyor: {theme_id}")
            db.collection('themes').document(theme_id).update({'is_active': True})
            logger.debug(f"Tema başarıyla aktifleştirildi: {theme_id}")
            return True
        except Exception as e:
            logger.error(f"Tema aktifleştirme hatası: {str(e)}", exc_info=True)
            return False
    
    async def create_theme(self, theme_data):
        """Yeni tema oluştur"""
        try:
            theme_ref = db.collection('themes').document()
            theme_id = theme_ref.id
            
            # Tema verilerini hazırla
            theme_data['id'] = theme_id
            theme_data['created_at'] = firestore.SERVER_TIMESTAMP
            theme_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            # Firestore'a kaydet - await kullanmadan düzeltildi
            theme_ref.set(theme_data)
            
            return theme_data
        except Exception as e:
            logger.error(f"Tema oluşturma hatası: {str(e)}", exc_info=True)
            return None
    
    async def update_theme(self, theme_id, theme_data):
        """Tema güncelle"""
        try:
            theme_data['updated_at'] = firestore.SERVER_TIMESTAMP
            await db.collection('themes').document(theme_id).update(theme_data)
            return True
        except Exception as e:
            logger.error(f"Tema güncelleme hatası: {str(e)}", exc_info=True)
            return False
    
    async def delete_theme(self, theme_id):
        """Tema sil"""
        try:
            # Tema aktif mi kontrol et
            theme_ref = await db.collection('themes').document(theme_id).get()
            if theme_ref.exists and theme_ref.to_dict().get('is_active', False):
                logger.error(f"Aktif tema silinemez: {theme_id}")
                return False
            
            # Tema dizinini sil
            theme_dir = os.path.join(self.themes_dir, theme_id)
            if os.path.exists(theme_dir):
                shutil.rmtree(theme_dir)
            
            # Veritabanından sil
            await db.collection('themes').document(theme_id).delete()
            return True
        except Exception as e:
            logger.error(f"Tema silme hatası: {str(e)}", exc_info=True)
            return False
    
    def process_theme_file(self, file):
        """Tema dosyasını işle"""
        try:
            filename = secure_filename(file.filename)
            temp_path = os.path.join(self.themes_dir, filename)
            
            # Dosyayı geçici olarak kaydet
            file.save(temp_path)
            
            # Dosya uzantısına göre işle
            if filename.endswith('.zip'):
                with zipfile.ZipFile(temp_path, 'r') as zip_ref:
                    # Tema adını zip dosyasından al
                    theme_name = os.path.splitext(filename)[0]
                    extract_path = os.path.join(self.themes_dir, theme_name)
                    
                    # Varsa eski temayı sil
                    if os.path.exists(extract_path):
                        shutil.rmtree(extract_path)
                    
                    # Temayı çıkart
                    zip_ref.extractall(extract_path)
                    
            elif filename.endswith('.rar'):
                if not unrar_path:
                    raise Exception("UnRAR.exe bulunamadı! RAR dosyaları açılamaz.")
                    
                with rarfile.RarFile(temp_path, 'r') as rar_ref:
                    # Tema adını rar dosyasından al
                    theme_name = os.path.splitext(filename)[0]
                    extract_path = os.path.join(self.themes_dir, theme_name)
                    
                    # Varsa eski temayı sil
                    if os.path.exists(extract_path):
                        shutil.rmtree(extract_path)
                    
                    # Temayı çıkart
                    rar_ref.extractall(extract_path)
            else:
                raise Exception("Desteklenmeyen dosya formatı! Sadece ZIP ve RAR dosyaları kabul edilir.")
            
            # Geçici dosyayı sil
            os.remove(temp_path)
            
            # theme.json dosyasını kontrol et
            theme_json_path = os.path.join(extract_path, 'theme.json')
            if not os.path.exists(theme_json_path):
                raise Exception("Geçersiz tema! theme.json dosyası bulunamadı.")
            
            return theme_name
            
        except Exception as e:
            logger.error(f"Tema işleme hatası: {str(e)}", exc_info=True)
            raise

    async def process_theme_directory(self, theme_dir):
        """Tema dizinini işle"""
        try:
            logger.debug(f"Tema dizini işleniyor: {theme_dir}")
            
            # Dizin içeriğini listele
            files = os.listdir(theme_dir)
            logger.debug(f"Dizin içeriği: {files}")
            
            # theme.json dosyasını kontrol et
            theme_json_path = os.path.join(theme_dir, 'theme.json')
            if not os.path.exists(theme_json_path):
                # Eğer ana dizinde theme.json yoksa, alt dizinlerde ara
                for root, dirs, files in os.walk(theme_dir):
                    for file in files:
                        if file == 'theme.json':
                            theme_json_path = os.path.join(root, file)
                            # theme.json'ı ana dizine taşı
                            with open(theme_json_path, 'r', encoding='utf-8') as f:
                                theme_data = json.load(f)
                            with open(os.path.join(theme_dir, 'theme.json'), 'w', encoding='utf-8') as f:
                                json.dump(theme_data, f, indent=4)
                            theme_json_path = os.path.join(theme_dir, 'theme.json')
                            break
                
                if not os.path.exists(theme_json_path):
                    logger.error("theme.json dosyası bulunamadı")
                    return None
            
            # Tema bilgilerini oku
            with open(theme_json_path, 'r', encoding='utf-8') as f:
                theme_data = json.load(f)
            
            logger.debug(f"Tema verileri: {theme_data}")
            
            # Gerekli alanları kontrol et
            required_fields = ['name', 'description', 'version', 'author']
            for field in required_fields:
                if field not in theme_data:
                    logger.error(f"Eksik alan: {field}")
                    return None
            
            # Tema dosyalarını themes dizinine kopyala
            theme_name = theme_data['name'].lower().replace(' ', '_')
            target_dir = os.path.join(self.themes_dir, theme_name)
            
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            
            # Tema dizinini kopyala
            shutil.copytree(theme_dir, target_dir)
            
            # Tema verilerini döndür
            return {
                'name': theme_data['name'],
                'description': theme_data['description'],
                'version': theme_data['version'],
                'author': theme_data['author'],
                'directory': theme_name,
                'is_active': False,
                'created_at': firestore.SERVER_TIMESTAMP
            }
            
        except Exception as e:
            logger.error(f"Tema dizini işleme hatası: {str(e)}", exc_info=True)
            return None 