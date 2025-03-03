from typing import Dict, Any, List, Optional
from app.modules.base import BaseModule
from datetime import datetime

class SliderModule(BaseModule):
    """Slider modülü için model sınıfı"""
    
    collection_name = 'sliders'
    
    def create_slider(self, title: str, image_url: str, link: str = None, 
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
        
        return self.create(slider_data)
    
    def update_slider(self, slider_id: str, data: Dict[str, Any]) -> bool:
        """Slider bilgilerini günceller"""
        data['updated_at'] = datetime.now()
        return self.update(slider_id, data)
    
    def activate_slider(self, slider_id: str) -> bool:
        """Slider'ı aktifleştirir"""
        return self.update(slider_id, {'is_active': True, 'updated_at': datetime.now()})
    
    def deactivate_slider(self, slider_id: str) -> bool:
        """Slider'ı deaktifleştirir"""
        return self.update(slider_id, {'is_active': False, 'updated_at': datetime.now()})
    
    def reorder_sliders(self, order_data: List[Dict[str, Any]]) -> bool:
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
    
    def get_active_sliders(self) -> List[Dict[str, Any]]:
        """Aktif slider'ları sıralı şekilde getirir"""
        return self.list(
            filters=[('is_active', '==', True)],
            order_by='order',
            direction='asc'
        )
        
    def get_all_sliders(self) -> List[Dict[str, Any]]:
        """Tüm slider'ları getirir"""
        return self.list(order_by='order', direction='asc')
