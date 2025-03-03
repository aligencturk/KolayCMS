from datetime import datetime
from app.modules.base import BaseModule

class HRModule(BaseModule):
    def __init__(self):
        super().__init__('hr_jobs')
        
    def get_all_jobs(self):
        """Tüm iş ilanlarını getir"""
        jobs = []
        docs = self.collection.order_by('created_at', direction='DESCENDING').stream()
        for doc in docs:
            job_data = doc.to_dict()
            job_data['id'] = doc.id
            jobs.append(job_data)
        return jobs
    
    def get_job_by_id(self, job_id):
        """ID'ye göre iş ilanı getir"""
        doc_ref = self.collection.document(job_id)
        doc = doc_ref.get()
        if doc.exists:
            job_data = doc.to_dict()
            job_data['id'] = doc.id
            return job_data
        return None
    
    def add_job(self, job_data):
        """Yeni iş ilanı ekle"""
        job_data['created_at'] = datetime.now()
        job_data['updated_at'] = datetime.now()
        doc_ref = self.collection.add(job_data)
        return doc_ref[1].id
    
    def update_job(self, job_id, job_data):
        """İş ilanını güncelle"""
        job_data['updated_at'] = datetime.now()
        doc_ref = self.collection.document(job_id)
        doc_ref.update(job_data)
        return job_id
    
    def delete_job(self, job_id):
        """İş ilanını sil"""
        doc_ref = self.collection.document(job_id)
        doc_ref.delete()
        return True
