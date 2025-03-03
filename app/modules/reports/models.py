from app.modules.base import BaseModule
from typing import Dict, Any, List, Optional
from datetime import datetime

class ReportModule(BaseModule):
    """Rapor modülü için model sınıfı"""
    
    collection_name = 'reports'
    
    def create_report(self, title: str, content: str, category: str, 
                     author_id: str, is_published: bool = False, 
                     tags: List[str] = None, file_url: str = None) -> Optional[str]:
        """Yeni bir rapor oluştur"""
        report_data = {
            'title': title,
            'content': content,
            'category': category,
            'author_id': author_id,
            'is_published': is_published,
            'tags': tags or [],
            'file_url': file_url,
            'view_count': 0,
            'created_at': datetime.now(),
            'updated_at': datetime.now()
        }
        
        return self.create(report_data)
    
    def get_all_reports(self) -> List[Dict[str, Any]]:
        """Tüm raporları getir"""
        return self.list()
    
    def update_report(self, report_id: str, data: Dict[str, Any]) -> bool:
        """Var olan bir raporu güncelle"""
        data['updated_at'] = datetime.now()
        return self.update(report_id, data)
    
    def publish_report(self, report_id: str) -> bool:
        """Raporu yayınla"""
        return self.update(report_id, {'is_published': True, 'updated_at': datetime.now()})
    
    def unpublish_report(self, report_id: str) -> bool:
        """Raporu yayından kaldır"""
        return self.update(report_id, {'is_published': False, 'updated_at': datetime.now()})
    
    def increment_view_count(self, report_id: str) -> bool:
        """Rapor görüntülenme sayısını artır"""
        report = self.get(report_id)
        if not report:
            return False
        
        current_count = report.get('view_count', 0)
        return self.update(report_id, {'view_count': current_count + 1})
    
    def get_by_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Belirli bir kategorideki raporları getir"""
        return self.list(filters=[('category', '==', category)], limit=limit)
    
    def get_published_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Yayınlanmış raporları getir"""
        return self.list(filters=[('is_published', '==', True)], 
                        order_by='created_at', limit=limit)
    
    def search_reports(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Raporlarda arama yap"""
        # Not: Firestore tam metin araması desteklemez, bu yüzden basit bir çözüm
        results = []
        all_reports = self.list(limit=100)  # Daha fazla rapor için sayfalama gerekebilir
        
        query = query.lower()
        for report in all_reports:
            if (query in report.get('title', '').lower() or 
                query in report.get('content', '').lower() or
                query in ' '.join(report.get('tags', [])).lower()):
                results.append(report)
                
                if len(results) >= limit:
                    break
                    
        return results
    
    def get_categories(self) -> List[str]:
        """Tüm rapor kategorilerini getir"""
        categories = set()
        reports = self.get_all_reports()
        
        for report in reports:
            category = report.get('category')
            if category:
                categories.add(category)
                
        return sorted(list(categories))
        
    def count_by_category(self, category: str) -> int:
        """Belirli bir kategorideki rapor sayısını getir"""
        reports = self.get_published_reports(category=category)
        return len(reports)
        
    def search(self, query: str) -> List[Dict[str, Any]]:
        """Raporlarda arama yap"""
        query = query.lower()
        results = []
        
        # Tüm raporları getir
        reports = self.get_all_reports()
        
        # Başlık, içerik, kategori ve etiketlerde arama yap
        for report in reports:
            title = report.get('title', '').lower()
            content = report.get('content', '').lower()
            category = report.get('category', '').lower()
            tags = report.get('tags', '').lower()
            
            if (query in title or query in content or 
                query in category or query in tags):
                results.append(report)
                
        return results
