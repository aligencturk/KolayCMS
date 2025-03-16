from datetime import datetime
from typing import Dict, Any, Optional
from slugify import slugify
from flask_login import UserMixin
import uuid
from app import db, login_manager

class BaseModel:
    def __init__(self, id: str = None, created_at: datetime = None, updated_at: datetime = None, created_by: str = None, updated_by: str = None):
        self.id = id or str(uuid.uuid4())
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.created_by = created_by
        self.updated_by = updated_by

    def to_dict(self) -> Dict[str, Any]:
        """Model verilerini dictionary'e dönüştür"""
        return {
            'id': self.id,
            'created_at': self.created_at.strftime('%a, %d %b %Y %H:%M:%S GMT') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%a, %d %b %Y %H:%M:%S GMT') if self.updated_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by
        }

    @staticmethod
    def parse_date(date_value) -> Optional[datetime]:
        """Tarih değerini datetime nesnesine dönüştür"""
        if isinstance(date_value, datetime):
            return date_value
        if isinstance(date_value, str):
            try:
                # RFC 2822 formatını dene
                return datetime.strptime(date_value, '%a, %d %b %Y %H:%M:%S GMT')
            except ValueError:
                try:
                    # ISO format dene
                    return datetime.fromisoformat(date_value.replace('Z', '+00:00'))
                except ValueError:
                    return None
        return None

class User(UserMixin):
    def __init__(self, uid, email, username, role='user'):
        self.uid = uid
        self.email = email
        self.username = username
        self.role = role
        self._authenticated = True
        
    @property
    def is_authenticated(self):
        return self._authenticated
        
    @property
    def is_active(self):
        return True
        
    @property
    def is_anonymous(self):
        return False
        
    def get_id(self):
        return str(self.uid)
        
    @property
    def is_admin(self):
        """Kullanıcının admin rolüne sahip olup olmadığını kontrol et"""
        return str(self.role).lower() == 'admin'
    
    @property
    def is_editor(self):
        """Kullanıcının editor rolüne sahip olup olmadığını kontrol et"""
        return str(self.role).lower() in ['editor', 'admin']
        
    def __repr__(self):
        return f'<User {self.email} (Role: {self.role})>'

class Report(BaseModel):
    def __init__(self, title: str, content: str, author_id: str, status: str = 'draft', **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.content = content
        self.author_id = author_id
        self.status = status
        self.slug = slugify(title)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'title': self.title,
            'content': self.content,
            'author_id': self.author_id,
            'status': self.status,
            'slug': self.slug
        })
        return data

class Slider(BaseModel):
    def __init__(self, title: str, image_url: str, link: str = None, order: int = 0, is_active: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.image_url = image_url
        self.link = link
        self.order = order
        self.is_active = is_active

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'title': self.title,
            'image_url': self.image_url,
            'link': self.link,
            'order': self.order,
            'is_active': self.is_active
        })
        return data

class Corporate(BaseModel):
    def __init__(self, title: str, content: str, page_type: str, meta_description: str = None, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.content = content
        self.page_type = page_type  # about, mission, vision, etc.
        self.meta_description = meta_description
        self.slug = slugify(title)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'title': self.title,
            'content': self.content,
            'page_type': self.page_type,
            'meta_description': self.meta_description,
            'slug': self.slug
        })
        return data

class TeamMember(BaseModel):
    def __init__(self, name: str, title: str, image_url: str = None, bio: str = None, 
                 email: str = None, social_media: Dict[str, str] = None, order: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.title = title
        self.image_url = image_url
        self.bio = bio
        self.email = email
        self.social_media = social_media or {}
        self.order = order

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'name': self.name,
            'title': self.title,
            'image_url': self.image_url,
            'bio': self.bio,
            'email': self.email,
            'social_media': self.social_media,
            'order': self.order
        })
        return data

class JobPosting(BaseModel):
    def __init__(self, title: str, description: str, requirements: list, 
                 location: str, employment_type: str, is_active: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.description = description
        self.requirements = requirements
        self.location = location
        self.employment_type = employment_type
        self.is_active = is_active
        self.slug = slugify(title)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'title': self.title,
            'description': self.description,
            'requirements': self.requirements,
            'location': self.location,
            'employment_type': self.employment_type,
            'is_active': self.is_active,
            'slug': self.slug
        })
        return data

class Service(BaseModel):
    def __init__(self, title: str, description: str, icon: str = None, 
                 image_url: str = None, features: list = None, order: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.description = description
        self.icon = icon
        self.image_url = image_url
        self.features = features or []
        self.order = order
        self.slug = slugify(title)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'image_url': self.image_url,
            'features': self.features,
            'order': self.order,
            'slug': self.slug
        })
        return data

class Project(BaseModel):
    """Proje modeli"""
    def __init__(self, title: str, description: str, category: str, 
                 image_urls: list = None, client: str = None, completion_date: datetime = None,
                 technologies: list = None, is_featured: bool = False, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.description = description
        self.category = category
        self.image_urls = image_urls or []
        self.client = client
        self.completion_date = completion_date
        self.technologies = technologies or []
        self.is_featured = is_featured
        self.slug = slugify(title)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'image_urls': self.image_urls,
            'client': self.client,
            'completion_date': self.completion_date,
            'technologies': self.technologies,
            'is_featured': self.is_featured,
            'slug': self.slug
        })
        return data

class Theme(BaseModel):
    """Tema modeli"""
    def __init__(self, name: str, description: str = "", author: str = "", version: str = "1.0.0",
                 is_active: bool = False, thumbnail_url: str = "", template_dir: str = "",
                 css_dir: str = "", js_dir: str = "", **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.author = author
        self.version = version
        self.is_active = is_active
        self.thumbnail_url = thumbnail_url
        self.template_dir = template_dir
        self.css_dir = css_dir
        self.js_dir = js_dir

    @staticmethod
    def from_dict(data: Dict[str, Any], id: str = None) -> Optional['Theme']:
        """Dictionary'den Theme nesnesi oluştur"""
        import logging
        logger = logging.getLogger(__name__)
        
        if not data:
            logger.error(f"Theme.from_dict: Veri yok (ID: {id})")
            return None
            
        try:
            logger.debug(f"Theme.from_dict başladı - ID: {id}")
            logger.debug(f"Gelen veri: {data}")
            
            # Gerekli alanları kontrol et
            required_fields = ['name']
            for field in required_fields:
                if field not in data:
                    logger.error(f"Theme.from_dict: Gerekli alan eksik - {field} (ID: {id})")
                    return None
            
            # Datetime dönüşümlerini yap
            created_at = BaseModel.parse_date(data.get('created_at'))
            updated_at = BaseModel.parse_date(data.get('updated_at'))
            
            if not created_at:
                created_at = datetime.now()
                logger.warning(f"Theme.from_dict: created_at alanı bulunamadı, varsayılan değer atandı (ID: {id})")
            
            if not updated_at:
                updated_at = datetime.now()
                logger.warning(f"Theme.from_dict: updated_at alanı bulunamadı, varsayılan değer atandı (ID: {id})")
            
            # BaseModel alanlarını ayır
            base_fields = {
                'id': id or data.get('id'),
                'created_at': created_at,
                'updated_at': updated_at,
                'created_by': data.get('created_by'),
                'updated_by': data.get('updated_by')
            }
            
            logger.debug(f"Base fields: {base_fields}")
            
            # Theme nesnesini oluştur
            theme = Theme(
                name=data.get('name', ''),
                description=data.get('description', ''),
                author=data.get('author', ''),
                version=data.get('version', '1.0.0'),
                is_active=bool(data.get('is_active', False)),
                thumbnail_url=data.get('thumbnail_url', ''),
                template_dir=data.get('template_dir', ''),
                css_dir=data.get('css_dir', ''),
                js_dir=data.get('js_dir', ''),
                **base_fields
            )
            
            logger.debug(f"Theme nesnesi oluşturuldu: {theme.name} (ID: {theme.id})")
            return theme
            
        except Exception as e:
            logger.error(f"Theme.from_dict hata oluştu (ID: {id}): {str(e)}", exc_info=True)
            return None

    def to_dict(self) -> Dict[str, Any]:
        """Theme nesnesini dictionary'e dönüştür"""
        data = super().to_dict()
        data.update({
            'name': self.name,
            'description': self.description,
            'author': self.author,
            'version': self.version,
            'is_active': bool(self.is_active),  # bool dönüşümü ekle
            'thumbnail_url': self.thumbnail_url,
            'template_dir': self.template_dir,
            'css_dir': self.css_dir,
            'js_dir': self.js_dir
        })
        return data

class ThemeTemplate:
    """Tema şablonu modeli"""
    def __init__(self, theme_id, name, description='', template_path='', thumbnail_url='', 
                 is_active=False, created_at=None, updated_at=None, id=None):
        self.id = id or str(uuid.uuid4())
        self.theme_id = theme_id
        self.name = name
        self.description = description
        self.template_path = template_path
        self.thumbnail_url = thumbnail_url
        self.is_active = is_active
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self):
        return {
            'theme_id': self.theme_id,
            'name': self.name,
            'description': self.description,
            'template_path': self.template_path,
            'thumbnail_url': self.thumbnail_url,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
        
    @staticmethod
    def from_dict(data, id=None):
        """Sözlükten tema şablonu nesnesi oluştur"""
        if not data:
            return None
            
        # Eğer data içinde 'id' varsa ve id parametresi de belirtilmişse, veri kopyasını oluşturup 'id' alanını kaldır
        if id is not None and 'id' in data:
            data_copy = data.copy()
            data_copy.pop('id', None)
            data = data_copy
            
        return ThemeTemplate(
            theme_id=data.get('theme_id'),
            name=data.get('name'),
            description=data.get('description', ''),
            template_path=data.get('template_path', ''),
            thumbnail_url=data.get('thumbnail_url', ''),
            is_active=data.get('is_active', False),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            id=id
        )

class ThemeComponent:
    """Tema bileşeni modeli"""
    def __init__(self, name, html_content, css_content='', js_content='', theme_id=None, 
                 component_type='section', is_global=False, thumbnail_url='', category='',
                 created_at=None, updated_at=None, id=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.html_content = html_content
        self.css_content = css_content
        self.js_content = js_content
        self.theme_id = theme_id  # None ise global komponent
        self.component_type = component_type  # section, header, footer, sidebar, vs.
        self.is_global = is_global  # True ise tüm temalar için kullanılabilir
        self.thumbnail_url = thumbnail_url
        self.category = category
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def to_dict(self):
        return {
            'name': self.name,
            'html_content': self.html_content,
            'css_content': self.css_content,
            'js_content': self.js_content,
            'theme_id': self.theme_id,
            'component_type': self.component_type,
            'is_global': self.is_global,
            'thumbnail_url': self.thumbnail_url,
            'category': self.category,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class Component(BaseModel):
    """Bileşen modeli"""
    def __init__(self, name: str, description: str = "", component_type: str = "custom",
                 html_content: str = "", css_content: str = "", js_content: str = "",
                 is_active: bool = True, order: int = 0, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.component_type = component_type  # header, footer, sidebar, custom, etc.
        self.html_content = html_content
        self.css_content = css_content
        self.js_content = js_content
        self.is_active = is_active
        self.order = order
        self.slug = slugify(name)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'name': self.name,
            'description': self.description,
            'component_type': self.component_type,
            'html_content': self.html_content,
            'css_content': self.css_content,
            'js_content': self.js_content,
            'is_active': self.is_active,
            'order': self.order,
            'slug': self.slug
        })
        return data

class PageTemplate(BaseModel):
    """Sayfa şablonu modeli"""
    def __init__(self, name: str, description: str = "", template_type: str = "page",
                 html_content: str = "", css_content: str = "", js_content: str = "",
                 is_active: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.template_type = template_type  # page, layout, component
        self.html_content = html_content
        self.css_content = css_content
        self.js_content = js_content
        self.is_active = is_active
        self.slug = slugify(name)

    def to_dict(self) -> Dict[str, Any]:
        result = super().to_dict()
        result.update({
            'name': self.name,
            'description': self.description,
            'template_type': self.template_type,
            'html_content': self.html_content,
            'css_content': self.css_content,
            'js_content': self.js_content,
            'is_active': self.is_active,
        })
        return result
        
    @staticmethod
    def from_dict(data, id=None):
        """Sözlükten sayfa şablonu nesnesi oluştur"""
        if not data:
            return None
            
        # Eğer data içinde 'id' varsa ve id parametresi de belirtilmişse, veri kopyasını oluşturup 'id' alanını kaldır
        if id is not None and 'id' in data:
            data_copy = data.copy()
            data_copy.pop('id', None)
            data = data_copy
            
        return PageTemplate(
            name=data.get('name', ''),
            description=data.get('description', ''),
            template_type=data.get('template_type', 'page'),
            html_content=data.get('html_content', ''),
            css_content=data.get('css_content', ''),
            js_content=data.get('js_content', ''),
            is_active=data.get('is_active', True),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            created_by=data.get('created_by'),
            updated_by=data.get('updated_by'),
            id=id
        )

class PageElement(BaseModel):
    """Sayfa elemanı modeli"""
    def __init__(self, page_id: str, element_type: str, content: Dict[str, Any] = None,
                 position: Dict[str, int] = None, is_active: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.page_id = page_id
        self.element_type = element_type  # text, image, slider, form, etc.
        self.content = content or {}
        self.position = position or {'x': 0, 'y': 0, 'width': 12, 'height': 1}
        self.is_active = is_active

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'page_id': self.page_id,
            'element_type': self.element_type,
            'content': self.content,
            'position': self.position,
            'is_active': self.is_active
        })
        return data

class PageStyle:
    def __init__(self, global_styles=None, element_styles=None, page_id=None, last_updated=None, is_published=False, id=None):
        self.global_styles = global_styles or {}
        self.element_styles = element_styles or {}
        self.page_id = page_id
        self.last_updated = last_updated
        self.is_published = is_published
        self.id = id

class ComponentCategory:
    def __init__(self, name, description='', icon='fa-folder', 
                 created_at=None, created_by=None, id=None):
        self.name = name
        self.description = description
        self.icon = icon  # Font Awesome ikon
        self.created_at = created_at
        self.created_by = created_by
        self.id = id 