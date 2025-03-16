from firebase_admin import firestore
from flask import current_app
from datetime import datetime
from app import db, logger

def get_user_by_id(user_id):
    """
    Kullanıcı ID'sine göre kullanıcıyı getirir
    """
    if not user_id:
        return None
    
    try:
        logger.debug(f"Kullanıcı getiriliyor: {user_id}")
        users_ref = db.collection('users').where('uid', '==', user_id).limit(1).stream()
        
        for user in users_ref:
            logger.debug(f"Kullanıcı bulundu: {user_id}")
            return {'id': user.id, **user.to_dict()}
        
        logger.warning(f"Kullanıcı bulunamadı: {user_id}")
        return None
    except Exception as e:
        logger.error(f"Kullanıcı getirme hatası: {str(e)}", exc_info=True)
        return None

def get_user_by_email(email):
    """
    E-posta adresine göre kullanıcıyı getirir
    """
    if not email:
        logger.warning("E-posta adresi boş")
        return None
    
    try:
        logger.debug(f"Kullanıcı e-posta ile aranıyor: {email}")
        users_ref = db.collection('users').where('email', '==', email).limit(1).stream()
        
        user_list = list(users_ref)  # Stream'i listeye çevir
        logger.debug(f"Bulunan kullanıcı sayısı: {len(user_list)}")
        
        if user_list:
            user = user_list[0]
            user_data = {'id': user.id, **user.to_dict()}
            logger.debug(f"Kullanıcı bulundu: {user_data}")
            return user_data
            
        logger.warning(f"Kullanıcı bulunamadı: {email}")
        return None
    except Exception as e:
        logger.error(f"Kullanıcı arama hatası: {str(e)}", exc_info=True)
        return None

def create_user(user_data):
    """
    Yeni kullanıcı oluşturur
    """
    try:
        logger.debug(f"Yeni kullanıcı oluşturuluyor: {user_data.get('email')}")
        now = datetime.now()
        
        # E-posta zaten kullanılıyor mu kontrol et
        existing_user = get_user_by_email(user_data.get('email'))
        if existing_user:
            return None, "Bu e-posta adresi zaten kullanılıyor."
        
        # Timestamp ekle
        user_data['created_at'] = now
        user_data['updated_at'] = now
        
        doc_ref = db.collection('users').document()
        doc_ref.set(user_data)
        logger.debug(f"Kullanıcı başarıyla oluşturuldu: {doc_ref.id}")
        
        return doc_ref.id, None
    except Exception as e:
        logger.error(f"Kullanıcı oluşturma hatası: {str(e)}", exc_info=True)
        return None, f"Kullanıcı oluşturulurken hata: {str(e)}"

def update_user(user_id, update_data):
    """
    Kullanıcı bilgilerini günceller
    """
    try:
        logger.debug(f"Kullanıcı güncelleniyor: {user_id}")
        update_data['updated_at'] = datetime.now()
        
        # E-posta değişiyorsa, zaten kullanılıyor mu kontrol et
        if 'email' in update_data:
            existing_user = get_user_by_email(update_data['email'])
            if existing_user and existing_user['id'] != user_id:
                return False, "Bu e-posta adresi zaten kullanılıyor."
        
        doc_ref = db.collection('users').document(user_id)
        doc_ref.update(update_data)
        logger.debug(f"Kullanıcı başarıyla güncellendi: {user_id}")
        return True, None
    except Exception as e:
        logger.error(f"Kullanıcı güncelleme hatası: {str(e)}", exc_info=True)
        return False, f"Kullanıcı güncellenirken hata: {str(e)}"

def delete_user(user_id):
    """
    Kullanıcıyı siler
    """
    try:
        logger.debug(f"Kullanıcı siliniyor: {user_id}")
        doc_ref = db.collection('users').document(user_id)
        doc_ref.delete()
        logger.debug(f"Kullanıcı başarıyla silindi: {user_id}")
        return True
    except Exception as e:
        logger.error(f"Kullanıcı silme hatası: {str(e)}", exc_info=True)
        return False

def list_users(limit=10, offset=0, role=None):
    """
    Kullanıcı listesini getirir
    """
    try:
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
        logger.error(f"list_users hatası: {str(e)}")
        return [] 