from app import db, logger

class MenuModule:
    def __init__(self):
        try:
            self.collection = db.collection('menus')
            logger.debug("menus koleksiyonu başarıyla başlatıldı")
        except Exception as e:
            logger.error(f"MenuModule başlatılırken hata: {str(e)}")
            raise

    async def get_all_menus(self):
        """Tüm menüleri getir"""
        try:
            menus = []
            docs = self.collection.stream()
            for doc in docs:
                menu_data = doc.to_dict()
                menu_data['id'] = doc.id
                menus.append(menu_data)
            return menus
        except Exception as e:
            logger.error(f"Menüler getirilirken hata: {str(e)}")
            return []

    async def create_menu(self, menu_data):
        """Yeni menü oluştur"""
        try:
            doc_ref = self.collection.add(menu_data)
            return doc_ref[1].id
        except Exception as e:
            logger.error(f"Menü oluşturulurken hata: {str(e)}")
            return None

    async def update_menu(self, menu_id, menu_data):
        """Menü güncelle"""
        try:
            self.collection.document(menu_id).update(menu_data)
            return True
        except Exception as e:
            logger.error(f"Menü güncellenirken hata: {str(e)}")
            return False

    async def delete_menu(self, menu_id):
        """Menü sil"""
        try:
            self.collection.document(menu_id).delete()
            return True
        except Exception as e:
            logger.error(f"Menü silinirken hata: {str(e)}")
            return False 