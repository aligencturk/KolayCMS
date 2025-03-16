from app import db, logger
from app.utils.firestore_manager import FirestoreManager
from typing import Dict, Any, List, Optional
from datetime import datetime

class ReportModule:
    def __init__(self):
        """Rapor modülünü başlat"""
        logger.debug("ReportModule başlatılıyor...")
        self.collection = 'reports'
        self.db = FirestoreManager()
        logger.debug(f"{self.collection} koleksiyonu başarıyla başlatıldı")

    async def get_all_reports(self):
        """Tüm raporları getir"""
        try:
            reports = await self.db.get_documents(self.collection)
            return reports
        except Exception as e:
            logger.error(f"Raporlar getirilirken hata: {str(e)}", exc_info=True)
            return []

    async def get_report(self, report_id):
        """Belirli bir raporu getir"""
        try:
            report = await self.db.get_document(self.collection, report_id)
            return report
        except Exception as e:
            logger.error(f"Rapor getirilirken hata: {str(e)}", exc_info=True)
            return None

    async def create_report(self, report_data):
        """Yeni rapor oluştur"""
        try:
            report_id = await self.db.add_document(self.collection, report_data)
            return report_id
        except Exception as e:
            logger.error(f"Rapor oluşturulurken hata: {str(e)}", exc_info=True)
            return None

    async def update_report(self, report_id, report_data):
        """Rapor güncelle"""
        try:
            success = await self.db.update_document(self.collection, report_id, report_data)
            return success
        except Exception as e:
            logger.error(f"Rapor güncellenirken hata: {str(e)}", exc_info=True)
            return False

    async def delete_report(self, report_id):
        """Rapor sil"""
        try:
            success = await self.db.delete_document(self.collection, report_id)
            return success
        except Exception as e:
            logger.error(f"Rapor silinirken hata: {str(e)}", exc_info=True)
            return False

    def get_all_reports(self) -> List[Dict[str, Any]]:
        """Tüm raporları getir"""
        try:
            logger.debug("Tüm raporlar getiriliyor...")
            reports = self.list()
            logger.debug(f"Toplam {len(reports)} rapor getirildi")
            return reports
        except Exception as e:
            logger.error(f"Raporlar getirilirken hata: {str(e)}", exc_info=True)
            return []
    
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
