from app import db, logger
from google.cloud import firestore
from datetime import datetime

class ComponentModule:
    def __init__(self):
        self.collection = db.collection('components')
        
    async def create_component(self, data):
        """Yeni bir bileşen oluştur"""
        try:
            component_ref = self.collection.document()
            await component_ref.set({
                'name': data['name'],
                'description': data.get('description', ''),
                'type': data['type'],
                'category': data['category'],
                'icon': data.get('icon', 'ri-code-line'),
                'html_template': data['html_template'],
                'css_styles': data.get('css_styles', ''),
                'js_script': data.get('js_script', ''),
                'properties': data.get('properties', {}),
                'is_active': True,
                'created_at': firestore.SERVER_TIMESTAMP,
                'updated_at': firestore.SERVER_TIMESTAMP
            })
            return True
        except Exception as e:
            logger.error(f"Bileşen oluşturma hatası: {str(e)}", exc_info=True)
            return False
            
    async def get_component(self, component_id):
        """Belirli bir bileşeni getir"""
        try:
            doc = await self.collection.document(component_id).get()
            if doc.exists:
                data = doc.to_dict()
                data['id'] = doc.id
                return data
            return None
        except Exception as e:
            logger.error(f"Bileşen getirme hatası: {str(e)}", exc_info=True)
            return None
            
    async def get_all_components(self, active_only=True):
        """Tüm bileşenleri getir"""
        try:
            query = self.collection
            if active_only:
                query = query.where('is_active', '==', True)
                
            docs = await query.get()
            components = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                components.append(data)
            return components
        except Exception as e:
            logger.error(f"Bileşenleri getirme hatası: {str(e)}", exc_info=True)
            return []
            
    async def get_components_by_category(self, category, active_only=True):
        """Kategoriye göre bileşenleri getir"""
        try:
            query = self.collection.where('category', '==', category)
            if active_only:
                query = query.where('is_active', '==', True)
                
            docs = await query.get()
            components = []
            for doc in docs:
                data = doc.to_dict()
                data['id'] = doc.id
                components.append(data)
            return components
        except Exception as e:
            logger.error(f"Kategori bileşenlerini getirme hatası: {str(e)}", exc_info=True)
            return []
            
    async def update_component(self, component_id, data):
        """Bileşeni güncelle"""
        try:
            component_ref = self.collection.document(component_id)
            doc = await component_ref.get()
            
            if not doc.exists:
                return False
                
            update_data = {
                'name': data.get('name', doc.get('name')),
                'description': data.get('description', doc.get('description', '')),
                'type': data.get('type', doc.get('type')),
                'category': data.get('category', doc.get('category')),
                'icon': data.get('icon', doc.get('icon')),
                'html_template': data.get('html_template', doc.get('html_template')),
                'css_styles': data.get('css_styles', doc.get('css_styles', '')),
                'js_script': data.get('js_script', doc.get('js_script', '')),
                'properties': data.get('properties', doc.get('properties', {})),
                'is_active': data.get('is_active', doc.get('is_active')),
                'updated_at': firestore.SERVER_TIMESTAMP
            }
            
            await component_ref.update(update_data)
            return True
        except Exception as e:
            logger.error(f"Bileşen güncelleme hatası: {str(e)}", exc_info=True)
            return False
            
    async def delete_component(self, component_id):
        """Bileşeni sil"""
        try:
            component_ref = self.collection.document(component_id)
            doc = await component_ref.get()
            
            if not doc.exists:
                return False
                
            await component_ref.delete()
            return True
        except Exception as e:
            logger.error(f"Bileşen silme hatası: {str(e)}", exc_info=True)
            return False
            
    async def render_component(self, component_id, properties=None):
        """Bileşeni render et"""
        try:
            component = await self.get_component(component_id)
            if not component:
                return None
                
            # Şablon değişkenlerini hazırla
            template_vars = {
                'id': component_id,
                'type': component['type'],
                **component.get('properties', {}),
                **(properties or {})
            }
            
            # HTML şablonunu render et
            from jinja2 import Template
            template = Template(component['html_template'])
            html = template.render(**template_vars)
            
            return {
                'html': html,
                'css': component.get('css_styles', ''),
                'js': component.get('js_script', '')
            }
        except Exception as e:
            logger.error(f"Bileşen render hatası: {str(e)}", exc_info=True)
            return None 