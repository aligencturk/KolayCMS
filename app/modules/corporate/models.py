from typing import Dict, Any, List, Optional
from app.modules.base import BaseModule
from datetime import datetime

class CorporateModule(BaseModule):
    """Kurumsal İçerik modülü için model sınıfı"""
    
    collection_name = 'corporate'
    
    def create_content(self, title: str, content: str, slug: str, 
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
        
        return self.create(content_data)
    
    def update_content(self, content_id: str, data: Dict[str, Any]) -> bool:
        """Kurumsal içerik bilgilerini günceller"""
        data['updated_at'] = datetime.now()
        return self.update(content_id, data)
    
    def publish_content(self, content_id: str) -> bool:
        """İçeriği yayınlar"""
        return self.update(content_id, {'is_published': True, 'updated_at': datetime.now()})
    
    def unpublish_content(self, content_id: str) -> bool:
        """İçeriği yayından kaldırır"""
        return self.update(content_id, {'is_published': False, 'updated_at': datetime.now()})
    
    def get_by_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        """Slug'a göre içerik getir"""
        query = self.db.collection(self.collection_name).where('slug', '==', slug).limit(1)
        docs = query.get()
        
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
            
        return None
    
    def get_published_contents(self) -> List[Dict[str, Any]]:
        """Yayınlanmış içerikleri getirir"""
        # İndeksli sorgu kullan
        return self.list(
            filters=[('is_published', '==', True)],
            order_by='created_at',
            direction='desc'
        )
        
    def get_all_contents(self) -> List[Dict[str, Any]]:
        """Tüm içerikleri getirir"""
        return self.list(order_by='created_at', direction='desc')

    def search(self, query: str) -> List[Dict[str, Any]]:
        """Kurumsal içerikte arama yap"""
        query = query.lower()
        results = []
        
        # Tüm içerikleri getir
        contents = self.get_all_contents()
        
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
