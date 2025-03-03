from firebase_admin import firestore
from flask import current_app
from datetime import datetime

def get_user_by_id(user_id):
    """
    Kullanıcı ID'sine göre kullanıcıyı getirir
    """
    if not user_id:
        return None
    
    try:
        db = firestore.client()
        user_doc = db.collection('users').document(user_id).get()
        
        if user_doc.exists:
            return user_doc.to_dict()
        return None
    except Exception as e:
        current_app.logger.error(f"get_user_by_id hatası: {str(e)}")
        return None

def get_user_by_email(email):
    """
    E-posta adresine göre kullanıcıyı getirir
    """
    if not email:
        return None
    
    try:
        db = firestore.client()
        users_ref = db.collection('users').where('email', '==', email).limit(1)
        users = users_ref.stream()
        
        for user in users:
            return {**user.to_dict(), 'id': user.id}
        return None
    except Exception as e:
        current_app.logger.error(f"get_user_by_email hatası: {str(e)}")
        return None

def create_user(username, email, password_hash, role='user'):
    """
    Yeni kullanıcı oluşturur
    """
    try:
        db = firestore.client()
        now = datetime.now()
        
        # E-posta zaten kullanılıyor mu kontrol et
        existing_user = get_user_by_email(email)
        if existing_user:
            return None, "Bu e-posta adresi zaten kullanılıyor."
        
        user_data = {
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'is_active': True,
            'created_at': now,
            'updated_at': now
        }
        
        new_user_ref = db.collection('users').document()
        new_user_ref.set(user_data)
        
        return new_user_ref.id, None
    except Exception as e:
        current_app.logger.error(f"create_user hatası: {str(e)}")
        return None, f"Kullanıcı oluşturulurken hata: {str(e)}"

def update_user(user_id, update_data):
    """
    Kullanıcı bilgilerini günceller
    """
    try:
        db = firestore.client()
        update_data['updated_at'] = datetime.now()
        
        # E-posta değişiyorsa, zaten kullanılıyor mu kontrol et
        if 'email' in update_data:
            existing_user = get_user_by_email(update_data['email'])
            if existing_user and existing_user['id'] != user_id:
                return False, "Bu e-posta adresi zaten kullanılıyor."
        
        db.collection('users').document(user_id).update(update_data)
        return True, None
    except Exception as e:
        current_app.logger.error(f"update_user hatası: {str(e)}")
        return False, f"Kullanıcı güncellenirken hata: {str(e)}"

def delete_user(user_id):
    """
    Kullanıcıyı siler
    """
    try:
        db = firestore.client()
        db.collection('users').document(user_id).delete()
        return True
    except Exception as e:
        current_app.logger.error(f"delete_user hatası: {str(e)}")
        return False

def list_users(limit=10, offset=0, role=None):
    """
    Kullanıcı listesini getirir
    """
    try:
        db = firestore.client()
        users_ref = db.collection('users')
        
        if role:
            users_ref = users_ref.where('role', '==', role)
        
        users_ref = users_ref.order_by('created_at', direction=firestore.Query.DESCENDING)
        
        if offset > 0:
            users_ref = users_ref.offset(offset)
        
        if limit > 0:
            users_ref = users_ref.limit(limit)
        
        users = []
        for user in users_ref.stream():
            user_data = user.to_dict()
            user_data['id'] = user.id
            users.append(user_data)
        
        return users
    except Exception as e:
        current_app.logger.error(f"list_users hatası: {str(e)}")
        return [] 