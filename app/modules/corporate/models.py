from typing import Dict, Any, List, Optional
from app.modules.base import BaseModule
from datetime import datetime
from app import db, logger
from app.utils.firestore_manager import FirestoreManager

class CorporateModule(BaseModule):
    """Kurumsal İçerik modülü için model sınıfı"""
    
    collection_name = 'corporate'
    
    def __init__(self):
        """Kurumsal modülünü başlat"""
        logger.debug("CorporateModule başlatılıyor...")
        super().__init__()
        self.db = FirestoreManager()
        logger.debug(f"{self.collection_name} koleksiyonu başarıyla başlatıldı")

    async def get_all_contents(self):
        """Tüm kurumsal içerikleri getir"""
        try:
            contents = await self.db.get_documents(self.collection_name)
            return contents
        except Exception as e:
            logger.error(f"Kurumsal içerikler getirilirken hata: {str(e)}", exc_info=True)
            return []

    async def get_content(self, content_id):
        """Belirli bir kurumsal içeriği getir"""
        try:
            content = await self.db.get_document(self.collection_name, content_id)
            return content
        except Exception as e:
            logger.error(f"Kurumsal içerik getirilirken hata: {str(e)}", exc_info=True)
            return None

    async def create_content(self, title: str, content: str, slug: str, 
                           meta_description: str = None, meta_keywords: str = None,
                           is_published: bool = False) -> Optional[str]:
        """Yeni bir kurumsal içerik oluşturur"""
        content_data = {
            'title': title,
            'content': content,
            'slug': slug,
            'meta_description': meta_description,
            'meta_keywords': meta_keywords,
            'is_published': is_published,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        try:
            content_id = await self.db.add_document(self.collection_name, content_data)
            return content_id
        except Exception as e:
            logger.error(f"Kurumsal içerik oluşturulurken hata: {str(e)}", exc_info=True)
            return None
    
    async def update_content(self, content_id: str, data: Dict[str, Any]) -> bool:
        """Kurumsal içerik bilgilerini günceller"""
        data['updated_at'] = datetime.now()
        try:
            success = await self.db.update_document(self.collection_name, content_id, data)
            return success
        except Exception as e:
            logger.error(f"Kurumsal içerik güncellenirken hata: {str(e)}", exc_info=True)
            return False
    
    async def publish_content(self, content_id: str) -> bool:
        """İçeriği yayınlar"""
        return await self.update_content(content_id, {'is_published': True, 'updated_at': datetime.now()})
    
    async def unpublish_content(self, content_id: str) -> bool:
        """İçeriği yayından kaldırır"""
        return await self.update_content(content_id, {'is_published': False, 'updated_at': datetime.now()})
    
    async def get_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Slug'a göre içerik getir"""
        query = self.db.collection(self.collection_name).where('slug', '==', slug).limit(1)
        docs = await query.get()
        
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
            
        return None
    
    async def get_published_contents(self) -> List[Dict[str, Any]]:
        """Yayınlanmış içerikleri getirir"""
        # İndeksli sorgu kullan
        return await self.list(
            filters=[('is_published', '==', True)],
            order_by='created_at',
            direction='desc'
        )
        
    async def search(self, query: str) -> List[Dict[str, Any]]:
        """Kurumsal içerikte arama yap"""
        query = query.lower()
        results = []
        
        # Tüm içerikleri getir
        contents = await self.get_all_contents()
        
        # Başlık, içerik ve meta bilgilerinde arama yap
        for content in contents:
            title = content.get('title', '').lower()
            content_text = content.get('content', '').lower()
            meta_desc = content.get('meta_description', '').lower()
            meta_keywords = content.get('meta_keywords', '').lower()
            
            if (query in title or query in content_text or 
                query in meta_desc or query in meta_keywords):
                results.append(content)
                
        return results

    async def delete_content(self, content_id):
        """Kurumsal içerik sil"""
        try:
            success = await self.db.delete_document(self.collection_name, content_id)
            return success
        except Exception as e:
            logger.error(f"Kurumsal içerik silinirken hata: {str(e)}", exc_info=True)
            return False
