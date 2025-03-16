from typing import Dict, Any, List, Optional
from app.modules.base import BaseModule
from datetime import datetime
from app import db, logger
from app.utils.firestore_manager import FirestoreManager

class SliderModule(BaseModule):
    """Slider modülü için model sınıfı"""
    
    collection_name = 'sliders'
    
    def __init__(self):
        """Slider modülünü başlat"""
        logger.debug("SliderModule başlatılıyor...")
        super().__init__()
        self.db = FirestoreManager()
        logger.debug(f"{self.collection_name} koleksiyonu başarıyla başlatıldı")

    async def get_all_sliders(self):
        """Tüm sliderları getir"""
        try:
            sliders = await self.db.get_documents(self.collection_name)
            return sliders
        except Exception as e:
            logger.error(f"Sliderlar getirilirken hata: {str(e)}", exc_info=True)
            return []

    async def get_slider(self, slider_id):
        """Belirli bir sliderı getir"""
        try:
            slider = await self.db.get_document(self.collection_name, slider_id)
            return slider
        except Exception as e:
            logger.error(f"Slider getirilirken hata: {str(e)}", exc_info=True)
            return None

    async def create_slider(self, title: str, image_url: str, link: str = None, 
                          description: str = None, order: int = 0, 
                          is_active: bool = True) -> Optional[str]:
        """Yeni bir slider oluşturur"""
        slider_data = {
            'title': title,
            'image_url': image_url,
            'link': link,
            'description': description,
            'order': order,
            'is_active': is_active,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        try:
            slider_id = await self.db.add_document(self.collection_name, slider_data)
            return slider_id
        except Exception as e:
            logger.error(f"Slider oluşturulurken hata: {str(e)}", exc_info=True)
            return None
    
    async def update_slider(self, slider_id: str, data: Dict[str, Any]) -> bool:
        """Slider bilgilerini günceller"""
        data['updated_at'] = datetime.now()
        try:
            success = await self.db.update_document(self.collection_name, slider_id, data)
            return success
        except Exception as e:
            logger.error(f"Slider güncellenirken hata: {str(e)}", exc_info=True)
            return False
    
    async def activate_slider(self, slider_id: str) -> bool:
        """Slider'ı aktifleştirir"""
        return await self.update(slider_id, {'is_active': True, 'updated_at': datetime.now()})
    
    async def deactivate_slider(self, slider_id: str) -> bool:
        """Slider'ı deaktifleştirir"""
        return await self.update(slider_id, {'is_active': False, 'updated_at': datetime.now()})
    
    async def reorder_sliders(self, order_data: List[Dict[str, Any]]) -> bool:
        """Slider'ların sırasını günceller
        
        Args:
            order_data: [{'id': 'slider_id', 'order': 1}, ...]
        """
        batch = self.db.batch()
        
        for item in order_data:
            slider_ref = self.collection.document(item['id'])
            batch.update(slider_ref, {
                'order': item['order'],
                'updated_at': datetime.now()
            })
        
        batch.commit()
        return True
    
    async def get_active_sliders(self) -> List[Dict[str, Any]]:
        """Aktif slider'ları sıralı şekilde getirir"""
        return await self.list(
            filters=[('is_active', '==', True)],
            order_by='order',
            direction='asc'
        )

    async def delete_slider(self, slider_id):
        """Slider sil"""
        try:
            success = await self.db.delete_document(self.collection_name, slider_id)
            return success
        except Exception as e:
            logger.error(f"Slider silinirken hata: {str(e)}", exc_info=True)
            return False
