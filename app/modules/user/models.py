from typing import Dict, Any, List, Optional
from datetime import datetime
import firebase_admin
from firebase_admin import firestore, auth
from app.models import User

class UserModule:
    """Kullanıcı yönetimi modülü"""
    
    def __init__(self):
        self.db = firestore.client()
        self.users_ref = self.db.collection('users')
    
    def get_all_users(self) -> List[User]:
        """Tüm kullanıcıları getir"""
        users = []
        docs = self.users_ref.stream()
        
        for doc in docs:
            user_data = doc.to_dict()
            user = User.from_dict(user_data, doc.id)
            users.append(user)
        
        return users
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """ID'ye göre kullanıcı getir"""
        doc = self.users_ref.document(user_id).get()
        if doc.exists:
            return User.from_dict(doc.to_dict(), doc.id)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """E-posta adresine göre kullanıcı getir"""
        query = self.users_ref.where('email', '==', email).limit(1)
        docs = query.stream()
        
        for doc in docs:
            return User.from_dict(doc.to_dict(), doc.id)
        
        return None
    
    def create_user(self, email: str, password: str, username: str, role: str = 'user') -> User:
        """Yeni kullanıcı oluştur"""
        # Firebase Authentication'da kullanıcı oluştur
        user_record = auth.create_user(
            email=email,
            password=password,
            display_name=username
        )
        
        # Firestore'da kullanıcı verilerini sakla
        user = User(
            uid=user_record.uid,
            email=email,
            username=username,
            role=role
        )
        
        self.users_ref.document(user_record.uid).set(user.to_dict())
        
        return user
    
    def create_user_with_id(self, uid: str, email: str, username: str, role: str = 'user') -> User:
        """Var olan ID ile kullanıcı oluştur"""
        # Firestore'da kullanıcı verilerini sakla
        user = User(
            uid=uid,
            email=email,
            username=username,
            role=role
        )
        
        self.users_ref.document(uid).set(user.to_dict())
        
        return user
    
    def update_user(self, user_id: str, data: Dict[str, Any]) -> Optional[User]:
        """Kullanıcı bilgilerini güncelle"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Güncellenebilir alanlar
        if 'username' in data:
            user.username = data['username']
        
        if 'role' in data:
            user.role = data['role']
        
        if 'is_active' in data:
            user.is_active = data['is_active']
        
        user.updated_at = datetime.now()
        
        # Firebase Authentication'da güncelleme
        auth_update = {}
        if 'username' in data:
            auth_update['display_name'] = data['username']
        
        if auth_update:
            auth.update_user(user_id, **auth_update)
        
        # Firestore'da güncelleme
        self.users_ref.document(user_id).update(user.to_dict())
        
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Kullanıcıyı sil"""
        try:
            # Firebase Authentication'dan sil
            auth.delete_user(user_id)
            
            # Firestore'dan sil
            self.users_ref.document(user_id).delete()
            
            return True
        except Exception as e:
            print(f"Kullanıcı silme hatası: {e}")
            return False
    
    def activate_user(self, user_id: str) -> Optional[User]:
        """Kullanıcıyı aktifleştir"""
        return self.update_user(user_id, {'is_active': True})
    
    def deactivate_user(self, user_id: str) -> Optional[User]:
        """Kullanıcıyı deaktif et"""
        return self.update_user(user_id, {'is_active': False})
    
    def change_password(self, user_id: str, new_password: str) -> bool:
        """Kullanıcı şifresini değiştir"""
        try:
            auth.update_user(user_id, password=new_password)
            return True
        except Exception as e:
            print(f"Şifre değiştirme hatası: {e}")
            return False 