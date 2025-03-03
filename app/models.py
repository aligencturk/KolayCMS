from datetime import datetime
from typing import Dict, Any, Optional
from slugify import slugify
from flask_login import UserMixin

class BaseModel:
    def __init__(self, id: str = None, created_at: datetime = None, updated_at: datetime = None):
        self.id = id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

class User(UserMixin):
    """Kullanıcı modeli"""
    
    def __init__(self, uid, email, username, role='user', is_active=True):
        self.id = uid
        self.email = email
        self.username = username
        self.role = role
        self._is_active = is_active
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def get_id(self):
        return self.id
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_editor(self):
        return self.role == 'editor' or self.role == 'admin'
    
    @property
    def is_active(self):
        return self._is_active
    
    @is_active.setter
    def is_active(self, value):
        self._is_active = value
    
    def to_dict(self):
        return {
            'uid': self.id,
            'email': self.email,
            'username': self.username,
            'role': self.role,
            'is_active': self.is_active,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @staticmethod
    def from_dict(data, uid):
        user = User(
            uid=uid,
            email=data.get('email'),
            username=data.get('username'),
            role=data.get('role', 'user'),
            is_active=data.get('is_active', True)
        )
        if 'created_at' in data:
            user.created_at = data['created_at']
        if 'updated_at' in data:
            user.updated_at = data['updated_at']
        return user

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
    """Tema modeli - Sitenin farklı görünümleri için"""
    def __init__(self, name: str, description: str, 
                 primary_color: str = "#00BCD4", secondary_color: str = "#f44336",
                 font_family: str = "sans-serif", is_active: bool = False, 
                 css_variables: Dict[str, str] = None, **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.font_family = font_family
        self.is_active = is_active
        self.css_variables = css_variables or {}
        self.slug = slugify(name)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'name': self.name,
            'description': self.description,
            'primary_color': self.primary_color,
            'secondary_color': self.secondary_color,
            'font_family': self.font_family,
            'is_active': self.is_active,
            'css_variables': self.css_variables,
            'slug': self.slug
        })
        return data

class PageTemplate(BaseModel):
    """Sayfa şablonu modeli - Özelleştirilebilir sayfa düzenleri için"""
    def __init__(self, name: str, description: str, html_structure: str,
                 template_type: str = "page", thumbnail_url: str = None,
                 available_slots: Dict[str, str] = None, is_system: bool = False,
                 **kwargs):
        super().__init__(**kwargs)
        self.name = name
        self.description = description
        self.html_structure = html_structure
        self.template_type = template_type  # "page", "blog", "product", vb.
        self.thumbnail_url = thumbnail_url
        self.available_slots = available_slots or {"content": "Ana İçerik Alanı"}
        self.is_system = is_system  # Sistem şablonu mu (silinemeyen)
        self.slug = slugify(name)

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'name': self.name,
            'description': self.description,
            'html_structure': self.html_structure,
            'template_type': self.template_type,
            'thumbnail_url': self.thumbnail_url,
            'available_slots': self.available_slots,
            'is_system': self.is_system,
            'slug': self.slug
        })
        return data

class PageElement(BaseModel):
    """Sürükle-bırak düzenleyici için sayfa elemanları"""
    def __init__(self, element_type: str, title: str, content: Dict[str, Any],
                 position: Dict[str, int] = None, style: Dict[str, str] = None,
                 page_id: str = None, **kwargs):
        super().__init__(**kwargs)
        self.element_type = element_type  # "text", "image", "button", "video", etc.
        self.title = title
        self.content = content  # element_type'a göre değişen içerik
        self.position = position or {'x': 0, 'y': 0, 'width': 12, 'height': 1}
        self.style = style or {}
        self.page_id = page_id

    def to_dict(self) -> Dict[str, Any]:
        data = super().to_dict()
        data.update({
            'element_type': self.element_type,
            'title': self.title,
            'content': self.content,
            'position': self.position,
            'style': self.style,
            'page_id': self.page_id
        })
        return data 