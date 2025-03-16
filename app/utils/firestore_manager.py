from typing import Dict, Any, List, Optional
from firebase_admin import firestore
from datetime import datetime

class FirestoreManager:
    def __init__(self):
        self.db = firestore.client()

    async def get_document(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Belirtilen koleksiyondan bir döküman getir"""
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f"Döküman getirme hatası: {e}")
            return None

    async def get_documents(self, collection: str, filters: List[tuple] = None, 
                          order_by: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Koleksiyondan filtrelenmiş dökümanları getir"""
        try:
            query = self.db.collection(collection)
            
            if filters:
                for field, op, value in filters:
                    query = query.where(field, op, value)
            
            if order_by:
                query = query.order_by(order_by)
            
            if limit:
                query = query.limit(limit)
            
            docs = query.stream()
            return [doc.to_dict() for doc in docs]
        except Exception as e:
            print(f"Dökümanları getirme hatası: {e}")
            return []

    async def add_document(self, collection: str, data: Dict[str, Any], doc_id: str = None) -> Optional[str]:
        """Yeni bir döküman ekle"""
        try:
            if doc_id:
                doc_ref = self.db.collection(collection).document(doc_id)
                data['updated_at'] = datetime.now()
                doc_ref.set(data)
                return doc_id
            else:
                data['created_at'] = datetime.now()
                data['updated_at'] = datetime.now()
                doc_ref = self.db.collection(collection).add(data)
                return doc_ref[1].id
        except Exception as e:
            print(f"Döküman ekleme hatası: {e}")
            return None

    async def update_document(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Var olan bir dökümanı güncelle"""
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            data['updated_at'] = datetime.now()
            doc_ref.update(data)
            return True
        except Exception as e:
            print(f"Döküman güncelleme hatası: {e}")
            return False

    async def delete_document(self, collection: str, doc_id: str) -> bool:
        """Bir dökümanı sil"""
        try:
            self.db.collection(collection).document(doc_id).delete()
            return True
        except Exception as e:
            print(f"Döküman silme hatası: {e}")
            return False

    async def get_real_time_updates(self, collection: str, callback):
        """Gerçek zamanlı veri güncellemelerini dinle"""
        try:
            def on_snapshot(doc_snapshot, changes, read_time):
                for change in changes:
                    if change.type.name == 'ADDED':
                        callback('added', change.document.to_dict())
                    elif change.type.name == 'MODIFIED':
                        callback('modified', change.document.to_dict())
                    elif change.type.name == 'REMOVED':
                        callback('removed', change.document.to_dict())

            return self.db.collection(collection).on_snapshot(on_snapshot)
        except Exception as e:
            print(f"Gerçek zamanlı güncelleme hatası: {e}")
            return None

    async def get_page_styles(self, page_id: str) -> Optional[Dict[str, Any]]:
        """Sayfa stillerini getir"""
        try:
            doc_ref = self.db.collection('page_styles').document(page_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f"Sayfa stilleri getirme hatası: {e}")
            return None

    async def save_page_styles(self, page_id: str, styles_data: Dict[str, Any], is_published: bool = False) -> bool:
        """Sayfa stillerini kaydet veya güncelle"""
        try:
            doc_ref = self.db.collection('page_styles').document(page_id)
            
            # Varolan veriyi kontrol et
            doc = doc_ref.get()
            
            # Verileri hazırla
            data = {
                'page_id': page_id,
                'element_styles': styles_data.get('element_styles', {}),
                'global_styles': styles_data.get('global_styles', {}),
                'is_published': is_published,
                'updated_at': datetime.now()
            }
            
            # Döküman varsa güncelle, yoksa oluştur
            if doc.exists:
                doc_ref.update(data)
            else:
                data['created_at'] = datetime.now()
                doc_ref.set(data)
                
            return True
        except Exception as e:
            print(f"Sayfa stilleri kaydetme hatası: {e}")
            return False

    async def get_template_styles(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Şablon stillerini getir"""
        try:
            doc_ref = self.db.collection('template_styles').document(template_id)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f"Şablon stilleri getirme hatası: {e}")
            return None
            
    async def save_template_styles(self, template_id: str, styles_data: Dict[str, Any]) -> bool:
        """Şablon stillerini kaydet veya güncelle"""
        try:
            doc_ref = self.db.collection('template_styles').document(template_id)
            
            # Varolan veriyi kontrol et
            doc = doc_ref.get()
            
            # Verileri hazırla
            data = {
                'template_id': template_id,
                'element_styles': styles_data.get('element_styles', {}),
                'global_styles': styles_data.get('global_styles', {}),
                'updated_at': datetime.now()
            }
            
            # Döküman varsa güncelle, yoksa oluştur
            if doc.exists:
                doc_ref.update(data)
            else:
                data['created_at'] = datetime.now()
                doc_ref.set(data)
                
            return True
        except Exception as e:
            print(f"Şablon stilleri kaydetme hatası: {e}")
            return False 