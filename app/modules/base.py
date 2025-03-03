from datetime import datetime
from typing import Dict, Any, Optional, List
from app import db

class BaseModule:
    collection_name: str = None
    
    def __init__(self):
        if not self.collection_name:
            raise ValueError("collection_name must be set in child class")
        self.collection = db.collection(self.collection_name)
    
    def create(self, data: Dict[str, Any]) -> str:
        """Yeni bir döküman oluştur"""
        data['created_at'] = datetime.now()
        data['updated_at'] = datetime.now()
        doc_ref = self.collection.document()
        doc_ref.set(data)
        return doc_ref.id
    
    def update(self, doc_id: str, data: Dict[str, Any]) -> bool:
        """Dökümanı güncelle"""
        data['updated_at'] = datetime.now()
        doc_ref = self.collection.document(doc_id)
        if doc_ref.get().exists:
            doc_ref.update(data)
            return True
        return False
    
    def delete(self, doc_id: str) -> bool:
        """Dökümanı sil"""
        doc_ref = self.collection.document(doc_id)
        if doc_ref.get().exists:
            doc_ref.delete()
            return True
        return False
    
    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Dökümanı ID'ye göre getir"""
        doc_ref = self.collection.document(doc_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None
    
    def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Dökümanı ID'ye göre getir (ID'yi içerecek şekilde)"""
        doc = self.get(doc_id)
        if doc:
            doc['id'] = doc_id
        return doc
    
    def list(self, limit: int = 10, order_by: str = 'created_at', direction: str = 'desc', 
             filters: List = None, offset: int = 0) -> list:
        """Dökümanları listele"""
        # Firestore direction formatını uygun şekilde dönüştür
        firestore_direction = 'DESCENDING' if direction.lower() == 'desc' else 'ASCENDING'
        
        # Sorgu oluştur
        query = self.collection
        
        # Filtreleri uygula
        if filters:
            for field, operator, value in filters:
                query = query.where(field, operator, value)
        
        # Sıralama uygula
        query = query.order_by(order_by, direction=firestore_direction)
        
        # Offset varsa atla
        if offset > 0:
            # Firestore'da offset kullanmak için önce limit belirleyip stream etmek gerekiyor
            # Sonra bu belgelerden offset kadarını atlayıp, kalan belgeleri döndürüyoruz
            all_docs = list(query.limit(offset + limit).stream())
            docs = all_docs[offset:offset + limit]
        else:
            # Offset yoksa normal limit uygula
            docs = list(query.limit(limit).stream())
        
        # Sonuçları döndür
        return [{'id': doc.id, **doc.to_dict()} for doc in docs]
    
    def count(self, filters: List = None) -> int:
        """Koleksiyondaki belge sayısını döndürür"""
        query = self.collection
        
        # Filtreleri uygula
        if filters:
            for field, operator, value in filters:
                query = query.where(field, operator, value)
                
        # Tüm belgeleri al ve sayısını döndür
        return len(list(query.stream())) 