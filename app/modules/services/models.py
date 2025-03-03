from datetime import datetime
from app.modules.base import BaseModule

class ServicesModule(BaseModule):
    def __init__(self):
        super().__init__('services')
        
    def get_all_services(self):
        """Tüm hizmetleri getir"""
        services = []
        docs = self.collection.order_by('created_at', direction='DESCENDING').stream()
        for doc in docs:
            service_data = doc.to_dict()
            service_data['id'] = doc.id
            services.append(service_data)
        return services
    
    def get_service_by_id(self, service_id):
        """ID'ye göre hizmet getir"""
        doc_ref = self.collection.document(service_id)
        doc = doc_ref.get()
        if doc.exists:
            service_data = doc.to_dict()
            service_data['id'] = doc.id
            return service_data
        return None
    
    def add_service(self, service_data):
        """Yeni hizmet ekle"""
        service_data['created_at'] = datetime.now()
        service_data['updated_at'] = datetime.now()
        doc_ref = self.collection.add(service_data)
        return doc_ref[1].id
    
    def update_service(self, service_id, service_data):
        """Hizmeti güncelle"""
        service_data['updated_at'] = datetime.now()
        doc_ref = self.collection.document(service_id)
        doc_ref.update(service_data)
        return service_id
    
    def delete_service(self, service_id):
        """Hizmeti sil"""
        doc_ref = self.collection.document(service_id)
        doc_ref.delete()
        return True
