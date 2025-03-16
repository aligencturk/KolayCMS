from datetime import datetime
from typing import Dict, Any, Optional, List
from app import db, logger
from firebase_admin import firestore
import time

class BaseModule:
    collection_name: str = None
    _max_retries = 3
    _retry_delay = 1  # saniye
    
    def __init__(self):
        logger.debug(f"{self.__class__.__name__} başlatılıyor...")
        if not self.collection_name:
            logger.error(f"{self.__class__.__name__} için collection_name tanımlanmamış")
            raise ValueError("collection_name must be set in child class")
            
        # Firebase bağlantısını kontrol et ve yeniden deneme
        retries = 0
        while retries < self._max_retries:
            try:
                if not db:
                    logger.warning("Firestore client başlatılmamış, yeniden deneniyor...")
                    time.sleep(self._retry_delay)
                    retries += 1
                    continue
                    
                self.collection = db.collection(self.collection_name)
                # Test sorgusu yap
                self.collection.limit(1).get()
                logger.debug(f"{self.collection_name} koleksiyonu başarıyla başlatıldı")
                break
            except Exception as e:
                logger.error(f"Firestore bağlantı hatası (deneme {retries + 1}/{self._max_retries}): {str(e)}")
                if retries >= self._max_retries - 1:
                    raise
                time.sleep(self._retry_delay)
                retries += 1
    
    def create(self, data: Dict[str, Any]) -> str:
        """Yeni bir döküman oluştur"""
        try:
            logger.debug(f"{self.collection_name} koleksiyonuna yeni döküman ekleniyor")
            data['created_at'] = firestore.SERVER_TIMESTAMP
            data['updated_at'] = firestore.SERVER_TIMESTAMP
            doc_ref = self.collection.document()
            doc_ref.set(data)
            logger.debug(f"Döküman başarıyla oluşturuldu: {doc_ref.id}")
            return doc_ref.id
        except Exception as e:
            logger.error(f"Document creation error: {str(e)}", exc_info=True)
            raise
    
    def update(self, doc_id: str, data: Dict[str, Any]) -> bool:
        """Dökümanı güncelle"""
        try:
            logger.debug(f"{self.collection_name}/{doc_id} dökümanı güncelleniyor")
            data['updated_at'] = firestore.SERVER_TIMESTAMP
            doc_ref = self.collection.document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                doc_ref.update(data)
                logger.debug(f"Döküman başarıyla güncellendi: {doc_id}")
                return True
            logger.warning(f"Güncellenecek döküman bulunamadı: {doc_id}")
            return False
        except Exception as e:
            logger.error(f"Document update error: {str(e)}", exc_info=True)
            return False
    
    def delete(self, doc_id: str) -> bool:
        """Dökümanı sil"""
        try:
            logger.debug(f"{self.collection_name}/{doc_id} dökümanı siliniyor")
            doc_ref = self.collection.document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                doc_ref.delete()
                logger.debug(f"Döküman başarıyla silindi: {doc_id}")
                return True
            logger.warning(f"Silinecek döküman bulunamadı: {doc_id}")
            return False
        except Exception as e:
            logger.error(f"Document deletion error: {str(e)}", exc_info=True)
            return False
    
    def get(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Dökümanı ID'ye göre getir"""
        try:
            logger.debug(f"{self.collection_name}/{doc_id} dökümanı getiriliyor")
            doc_ref = self.collection.document(doc_id)
            doc = doc_ref.get()
            if doc.exists:
                logger.debug(f"Döküman başarıyla getirildi: {doc_id}")
                return doc.to_dict()
            logger.warning(f"Döküman bulunamadı: {doc_id}")
            return None
        except Exception as e:
            logger.error(f"Document get error: {str(e)}", exc_info=True)
            return None
    
    def get_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Dökümanı ID'ye göre getir (ID'yi içerecek şekilde)"""
        try:
            logger.debug(f"{self.collection_name}/{doc_id} dökümanı ID ile getiriliyor")
            doc = self.get(doc_id)
            if doc:
                doc['id'] = doc_id
                logger.debug(f"Döküman başarıyla getirildi: {doc_id}")
                return doc
            logger.warning(f"Döküman bulunamadı: {doc_id}")
            return None
        except Exception as e:
            logger.error(f"Document get_by_id error: {str(e)}", exc_info=True)
            return None
    
    def list(self, limit: int = None, order_by: str = 'created_at', direction: str = 'desc', 
             filters: List = None, offset: int = 0) -> list:
        """Dökümanları listele"""
        try:
            logger.debug(f"{self.collection_name} koleksiyonu listeleniyor")
            logger.debug(f"Parametreler: limit={limit}, order_by={order_by}, direction={direction}, filters={filters}, offset={offset}")
            
            # Firestore direction formatını uygun şekilde dönüştür
            firestore_direction = firestore.Query.DESCENDING if direction.lower() == 'desc' else firestore.Query.ASCENDING
            
            # Sorgu oluştur
            query = self.collection
            
            # Filtreleri uygula
            if filters:
                for field, operator, value in filters:
                    query = query.where(field, operator, value)
                    logger.debug(f"Filtre uygulandı: {field} {operator} {value}")
            
            # Sıralama uygula
            query = query.order_by(order_by, direction=firestore_direction)
            logger.debug(f"Sıralama uygulandı: {order_by} {direction}")
            
            # Offset varsa atla
            if offset > 0:
                logger.debug(f"Offset uygulanıyor: {offset}")
                if limit:
                    all_docs = list(query.limit(offset + limit).stream())
                    docs = all_docs[offset:offset + limit]
                else:
                    all_docs = list(query.stream())
                    docs = all_docs[offset:]
            else:
                if limit:
                    docs = list(query.limit(limit).stream())
                else:
                    docs = list(query.stream())
            
            # Sonuçları döndür
            result = [{'id': doc.id, **doc.to_dict()} for doc in docs]
            logger.debug(f"Toplam {len(result)} döküman listelendi")
            return result
        except Exception as e:
            logger.error(f"Document list error: {str(e)}", exc_info=True)
            return []
    
    def count(self, filters: List = None) -> int:
        """Koleksiyondaki belge sayısını döndürür"""
        try:
            logger.debug(f"{self.collection_name} koleksiyonu sayılıyor")
            query = self.collection
            
            # Filtreleri uygula
            if filters:
                for field, operator, value in filters:
                    query = query.where(field, operator, value)
                    logger.debug(f"Filtre uygulandı: {field} {operator} {value}")
                    
            # Tüm belgeleri al ve sayısını döndür
            count = len(list(query.stream()))
            logger.debug(f"Toplam {count} döküman sayıldı")
            return count
        except Exception as e:
            logger.error(f"Document count error: {str(e)}", exc_info=True)
            return 0 