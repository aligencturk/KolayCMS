from typing import Dict, Any, List, Optional
from app.utils.firestore_manager import FirestoreManager
from app.utils.validators import validate_content_data, validate_image_url, ValidationError

class ContentService:
    def __init__(self):
        self.db = FirestoreManager()
        self.collections = {
            'slider': 'sliders',
            'corporate': 'corporate_pages',
            'team': 'team_members',
            'job': 'job_postings',
            'service': 'services',
            'project': 'projects',
            'users': 'users'
        }

    async def create_content(self, content_type: str, data: Dict[str, Any]) -> Optional[str]:
        """Yeni içerik oluştur"""
        try:
            # İçerik verilerini doğrula
            validate_content_data(data)
            
            # Resim URL'si varsa doğrula
            if 'image_url' in data:
                validate_image_url(data['image_url'])
            
            # Koleksiyon adını al
            collection = self.collections.get(content_type)
            if not collection:
                raise ValidationError(f"Geçersiz içerik tipi: {content_type}")
            
            # Dökümanı ekle
            return await self.db.add_document(collection, data)
        except ValidationError as e:
            print(f"Doğrulama hatası: {e}")
            return None
        except Exception as e:
            print(f"İçerik oluşturma hatası: {e}")
            return None

    async def update_content(self, content_type: str, content_id: str, data: Dict[str, Any]) -> bool:
        """İçeriği güncelle"""
        try:
            # İçerik verilerini doğrula
            if 'title' in data or 'content' in data:
                validate_content_data(data)
            
            # Resim URL'si varsa doğrula
            if 'image_url' in data:
                validate_image_url(data['image_url'])
            
            # Koleksiyon adını al
            collection = self.collections.get(content_type)
            if not collection:
                raise ValidationError(f"Geçersiz içerik tipi: {content_type}")
            
            # Dökümanı güncelle
            return await self.db.update_document(collection, content_id, data)
        except ValidationError as e:
            print(f"Doğrulama hatası: {e}")
            return False
        except Exception as e:
            print(f"İçerik güncelleme hatası: {e}")
            return False

    async def delete_content(self, content_type: str, content_id: str) -> bool:
        """İçeriği sil"""
        try:
            collection = self.collections.get(content_type)
            if not collection:
                raise ValidationError(f"Geçersiz içerik tipi: {content_type}")
            
            return await self.db.delete_document(collection, content_id)
        except Exception as e:
            print(f"İçerik silme hatası: {e}")
            return False

    async def get_content(self, content_type: str, content_id: str) -> Optional[Dict[str, Any]]:
        """Belirli bir içeriği getir"""
        try:
            collection = self.collections.get(content_type)
            if not collection:
                raise ValidationError(f"Geçersiz içerik tipi: {content_type}")
            
            return await self.db.get_document(collection, content_id)
        except Exception as e:
            print(f"İçerik getirme hatası: {e}")
            return None

    async def list_contents(self, content_type: str, filters: List[tuple] = None, 
                          order_by: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """İçerikleri listele"""
        try:
            collection = self.collections.get(content_type)
            if not collection:
                raise ValidationError(f"Geçersiz içerik tipi: {content_type}")
            
            return await self.db.get_documents(collection, filters, order_by, limit)
        except Exception as e:
            print(f"İçerik listeleme hatası: {e}")
            return []

    async def subscribe_to_changes(self, content_type: str, callback):
        """İçerik değişikliklerini dinle"""
        try:
            collection = self.collections.get(content_type)
            if not collection:
                raise ValidationError(f"Geçersiz içerik tipi: {content_type}")
            
            return await self.db.get_real_time_updates(collection, callback)
        except Exception as e:
            print(f"İçerik değişikliği dinleme hatası: {e}")
            return None 