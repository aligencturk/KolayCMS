from typing import Dict, Any, List, Optional
from app import db, logger
from app.utils.firestore_manager import FirestoreManager
from datetime import datetime

class TeamModule:
    def __init__(self):
        """Ekip modülünü başlat"""
        logger.debug("TeamModule başlatılıyor...")
        self.collection = 'team_members'
        self.db = FirestoreManager()
        logger.debug(f"{self.collection} koleksiyonu başarıyla başlatıldı")

    async def get_active_members(self):
        """Aktif ekip üyelerini getir"""
        try:
            members = await self.db.get_documents(
                self.collection,
                filters=[('is_active', '==', True)],
                order_by='order'
            )
            return members
        except Exception as e:
            logger.error(f"Aktif ekip üyeleri getirilirken hata: {str(e)}", exc_info=True)
            return []

    async def get_member(self, member_id):
        """Belirli bir ekip üyesini getir"""
        try:
            member = await self.db.get_document(self.collection, member_id)
            return member
        except Exception as e:
            logger.error(f"Ekip üyesi getirilirken hata: {str(e)}", exc_info=True)
            return None

    async def create_member(self, member_data):
        """Yeni ekip üyesi oluştur"""
        try:
            member_id = await self.db.add_document(self.collection, member_data)
            return member_id
        except Exception as e:
            logger.error(f"Ekip üyesi oluşturulurken hata: {str(e)}", exc_info=True)
            return None

    async def update_member(self, member_id, member_data):
        """Ekip üyesi güncelle"""
        try:
            success = await self.db.update_document(self.collection, member_id, member_data)
            return success
        except Exception as e:
            logger.error(f"Ekip üyesi güncellenirken hata: {str(e)}", exc_info=True)
            return False

    async def delete_member(self, member_id):
        """Ekip üyesi sil"""
        try:
            success = await self.db.delete_document(self.collection, member_id)
            return success
        except Exception as e:
            logger.error(f"Ekip üyesi silinirken hata: {str(e)}", exc_info=True)
            return False

    def create_member(self, name: str, position: str, photo_url: str = None, 
                      bio: str = None, email: str = None, phone: str = None,
                      social_media: Dict[str, str] = None, order: int = 0,
                      is_active: bool = True) -> Optional[str]:
        """Yeni bir ekip üyesi oluşturur"""
        member_data = {
            'name': name,
            'position': position,
            'photo_url': photo_url,
            'bio': bio,
            'email': email,
            'phone': phone,
            'social_media': social_media or {},
            'order': order,
            'is_active': is_active,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        return self.create_member(member_data)
    
    def update_member(self, member_id: str, data: Dict[str, Any]) -> bool:
        """Ekip üyesi bilgilerini günceller"""
        data['updated_at'] = datetime.now()
        return self.update_member(member_id, data)
    
    def activate_member(self, member_id: str) -> bool:
        """Ekip üyesini aktifleştirir"""
        return self.update_member(member_id, {'is_active': True, 'updated_at': datetime.now()})
    
    def deactivate_member(self, member_id: str) -> bool:
        """Ekip üyesini deaktifleştirir"""
        return self.update_member(member_id, {'is_active': False, 'updated_at': datetime.now()})
    
    def reorder_members(self, order_data: List[Dict[str, Any]]) -> bool:
        """Ekip üyelerinin sırasını günceller
        
        Args:
            order_data: [{'id': 'member_id', 'order': 1}, ...]
        """
        batch = self.db.batch()
        
        for item in order_data:
            member_ref = self.db.collection(self.collection).document(item['id'])
            batch.update(member_ref, {
                'order': item['order'],
                'updated_at': datetime.now()
            })
        
        batch.commit()
        return True
    
    def get_active_members(self) -> List[Dict[str, Any]]:
        """Aktif ekip üyelerini sıralı şekilde getirir"""
        # İndeksli sorgu kullan
        return self.list(
            filters=[('is_active', '==', True)],
            order_by='order',
            direction='asc'
        )
            
    def get_member(self, member_id: str) -> Optional[Dict[str, Any]]:
        """Belirli bir ekip üyesini getir"""
        doc_ref = self.db.collection(self.collection).document(member_id)
        doc = doc_ref.get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
        
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Ekip üyelerinde arama yap"""
        query = query.lower()
        results = []
        
        # Tüm ekip üyelerini getir
        members = self.get_all_members()
        
        # İsim ve pozisyonda arama yap
        for member in members:
            name = member.get('name', '').lower()
            position = member.get('position', '').lower()
            bio = member.get('bio', '').lower()
            
            if query in name or query in position or query in bio:
                results.append(member)
                
        return results
