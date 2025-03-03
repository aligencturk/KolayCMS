from datetime import datetime
from app.modules.base import BaseModule

class ProjectsModule(BaseModule):
    def __init__(self):
        super().__init__('projects')
        
    def get_all_projects(self):
        """Tüm projeleri getir"""
        projects = []
        docs = self.collection.order_by('created_at', direction='DESCENDING').stream()
        for doc in docs:
            project_data = doc.to_dict()
            project_data['id'] = doc.id
            projects.append(project_data)
        return projects
    
    def get_project_by_id(self, project_id):
        """ID'ye göre proje getir"""
        doc_ref = self.collection.document(project_id)
        doc = doc_ref.get()
        if doc.exists:
            project_data = doc.to_dict()
            project_data['id'] = doc.id
            return project_data
        return None
    
    def add_project(self, project_data):
        """Yeni proje ekle"""
        project_data['created_at'] = datetime.now()
        project_data['updated_at'] = datetime.now()
        doc_ref = self.collection.add(project_data)
        return doc_ref[1].id
    
    def update_project(self, project_id, project_data):
        """Projeyi güncelle"""
        project_data['updated_at'] = datetime.now()
        doc_ref = self.collection.document(project_id)
        doc_ref.update(project_data)
        return project_id
    
    def delete_project(self, project_id):
        """Projeyi sil"""
        doc_ref = self.collection.document(project_id)
        doc_ref.delete()
        return True
