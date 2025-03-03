from typing import Dict, Any, List, Optional
from datetime import datetime
import re

class ValidationError(Exception):
    pass

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """Zorunlu alanları kontrol et"""
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        raise ValidationError(f"Zorunlu alanlar eksik: {', '.join(missing_fields)}")

def validate_email(email: str) -> bool:
    """Email formatını kontrol et"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_url(url: str) -> bool:
    """URL formatını kontrol et"""
    pattern = r'^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$'
    return bool(re.match(pattern, url))

def validate_date(date_str: str) -> Optional[datetime]:
    """Tarih formatını kontrol et ve datetime nesnesine çevir"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None

def validate_user_data(data: Dict[str, Any]) -> None:
    """Kullanıcı verilerini doğrula"""
    validate_required_fields(data, ['username', 'email'])
    if not validate_email(data['email']):
        raise ValidationError("Geçersiz email formatı")
    if data.get('role') and data['role'] not in ['admin', 'editor', 'user']:
        raise ValidationError("Geçersiz kullanıcı rolü")

def validate_content_data(data: Dict[str, Any]) -> None:
    """İçerik verilerini doğrula"""
    validate_required_fields(data, ['title', 'content'])
    if len(data['title']) < 3:
        raise ValidationError("Başlık en az 3 karakter olmalıdır")
    if len(data['content']) < 10:
        raise ValidationError("İçerik en az 10 karakter olmalıdır")

def validate_image_url(image_url: str) -> None:
    """Resim URL'sini doğrula"""
    if not validate_url(image_url):
        raise ValidationError("Geçersiz resim URL'si")
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    if not any(image_url.lower().endswith(ext) for ext in allowed_extensions):
        raise ValidationError("Desteklenmeyen resim formatı")

def validate_slug(slug: str) -> None:
    """Slug formatını doğrula"""
    if not re.match(r'^[a-z0-9]+(?:-[a-z0-9]+)*$', slug):
        raise ValidationError("Geçersiz slug formatı") 