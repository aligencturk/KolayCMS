from app.modules.base import BaseModule
from typing import Dict, Any, Optional

class UserModule(BaseModule):
    collection_name = 'users'
    
    def create_user(self, username: str, email: str, role: str = 'user') -> str:
        """Yeni bir kullanıcı oluştur"""
        data = {
            'username': username,
            'email': email,
            'role': role,
            'is_active': True
        }
        return self.create(data)
    
    def get_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Email ile kullanıcı getir"""
        users = self.collection.where('email', '==', email).limit(1).stream()
        for user in users:
            return {'id': user.id, **user.to_dict()}
        return None
    
    def update_role(self, user_id: str, new_role: str) -> bool:
        """Kullanıcı rolünü güncelle"""
        return self.update(user_id, {'role': new_role})
    
    def deactivate_user(self, user_id: str) -> bool:
        """Kullanıcıyı deaktif et"""
        return self.update(user_id, {'is_active': False})
    
    def activate_user(self, user_id: str) -> bool:
        """Kullanıcıyı aktif et"""
        return self.update(user_id, {'is_active': True})
    
    def is_admin(self) -> bool:
        """Kullanıcının admin rolüne sahip olup olmadığını kontrol et"""
        return self.role == 'admin'
    
    def is_editor(self) -> bool:
        """Kullanıcının editor rolüne sahip olup olmadığını kontrol et"""
        return self.role in ['editor', 'admin'] 