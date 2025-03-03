from flask import Blueprint, jsonify, request, current_app
from app.modules.team.models import TeamModule
from app.modules.sliders.models import SliderModule
from app.modules.corporate.models import CorporateModule
from app.modules.reports.models import ReportModule
from functools import wraps
import jwt
import datetime

# API Blueprint
api_bp = Blueprint('api', __name__, url_prefix='/wp-json/api/v1')

# Modülleri başlat
team_module = TeamModule()
slider_module = SliderModule()
corporate_module = CorporateModule()
report_module = ReportModule()

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token gerekli!'}), 401
        
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'message': 'Geçersiz token!'}), 401
        
        return f(*args, **kwargs)
    
    return decorated

# Token alma endpoint'i
@api_bp.route('/token', methods=['POST'])
def get_token():
    auth = request.authorization
    
    if not auth or not auth.username or not auth.password:
        return jsonify({'message': 'Kimlik doğrulama başarısız!'}), 401
    
    # Burada kullanıcı adı ve şifre kontrolü yapılmalı
    # Örnek olarak basit bir kontrol:
    if auth.username == current_app.config.get('API_USERNAME') and auth.password == current_app.config.get('API_PASSWORD'):
        token = jwt.encode({
            'user': auth.username,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, current_app.config['SECRET_KEY'], algorithm="HS256")
        
        return jsonify({'token': token})
    
    return jsonify({'message': 'Kimlik doğrulama başarısız!'}), 401

# Ekip Üyeleri API Endpoint'leri
@api_bp.route('/team', methods=['GET'])
def get_team_members():
    """Tüm ekip üyelerini getir (WP REST API uyumlu)"""
    members = team_module.get_active_members()
    
    # WP REST API formatına dönüştür
    formatted_members = []
    for member in members:
        formatted_members.append({
            'id': member.get('id'),
            'name': member.get('name'),
            'position': member.get('position'),
            'bio': member.get('bio'),
            'email': member.get('email'),
            'phone': member.get('phone'),
            'photo_url': member.get('photo_url'),
            'social_media': {
                'facebook': member.get('facebook', ''),
                'twitter': member.get('twitter', ''),
                'instagram': member.get('instagram', ''),
                'linkedin': member.get('linkedin', '')
            },
            'order': member.get('order', 0),
            'date': member.get('created_at', ''),
            'modified': member.get('updated_at', '')
        })
    
    return jsonify(formatted_members)

@api_bp.route('/team/<member_id>', methods=['GET'])
def get_team_member(member_id):
    """Belirli bir ekip üyesini getir (WP REST API uyumlu)"""
    member = team_module.get_member(member_id)
    
    if not member:
        return jsonify({'message': 'Ekip üyesi bulunamadı!'}), 404
    
    # WP REST API formatına dönüştür
    formatted_member = {
        'id': member.get('id'),
        'name': member.get('name'),
        'position': member.get('position'),
        'bio': member.get('bio'),
        'email': member.get('email'),
        'phone': member.get('phone'),
        'photo_url': member.get('photo_url'),
        'social_media': member.get('social_media', {}),
        'order': member.get('order', 0),
        'date': member.get('created_at', ''),
        'modified': member.get('updated_at', '')
    }
    
    return jsonify(formatted_member)

# Slider API Endpoint'leri
@api_bp.route('/sliders', methods=['GET'])
def get_sliders():
    """Tüm sliderları getir (WP REST API uyumlu)"""
    sliders = slider_module.get_active_sliders()
    
    # WP REST API formatına dönüştür
    formatted_sliders = []
    for slider in sliders:
        formatted_sliders.append({
            'id': slider.get('id'),
            'title': slider.get('title'),
            'description': slider.get('description'),
            'image_url': slider.get('image_url'),
            'link': slider.get('link'),
            'order': slider.get('order', 0),
            'date': slider.get('created_at', ''),
            'modified': slider.get('updated_at', '')
        })
    
    return jsonify(formatted_sliders)

@api_bp.route('/sliders/<slider_id>', methods=['GET'])
def get_slider(slider_id):
    """Belirli bir sliderı getir (WP REST API uyumlu)"""
    slider = slider_module.get(slider_id)
    
    if not slider:
        return jsonify({'message': 'Slider bulunamadı!'}), 404
    
    # WP REST API formatına dönüştür
    formatted_slider = {
        'id': slider.get('id'),
        'title': slider.get('title'),
        'description': slider.get('description'),
        'image_url': slider.get('image_url'),
        'link': slider.get('link'),
        'order': slider.get('order', 0),
        'date': slider.get('created_at', ''),
        'modified': slider.get('updated_at', '')
    }
    
    return jsonify(formatted_slider)

# Kurumsal İçerik API Endpoint'leri
@api_bp.route('/corporate', methods=['GET'])
def get_corporate_contents():
    """Tüm kurumsal içerikleri getir (WP REST API uyumlu)"""
    contents = corporate_module.get_published_contents()
    
    # WP REST API formatına dönüştür
    formatted_contents = []
    for content in contents:
        formatted_contents.append({
            'id': content.get('id'),
            'title': content.get('title'),
            'content': content.get('content'),
            'slug': content.get('slug'),
            'meta': {
                'description': content.get('meta_description', ''),
                'keywords': content.get('meta_keywords', '')
            },
            'date': content.get('created_at', ''),
            'modified': content.get('updated_at', '')
        })
    
    return jsonify(formatted_contents)

@api_bp.route('/corporate/<content_id>', methods=['GET'])
def get_corporate_content(content_id):
    """Belirli bir kurumsal içeriği getir (WP REST API uyumlu)"""
    content = corporate_module.get(content_id)
    
    if not content:
        return jsonify({'message': 'İçerik bulunamadı!'}), 404
    
    # WP REST API formatına dönüştür
    formatted_content = {
        'id': content.get('id'),
        'title': content.get('title'),
        'content': content.get('content'),
        'slug': content.get('slug'),
        'meta': {
            'description': content.get('meta_description', ''),
            'keywords': content.get('meta_keywords', '')
        },
        'date': content.get('created_at', ''),
        'modified': content.get('updated_at', '')
    }
    
    return jsonify(formatted_content)

@api_bp.route('/corporate/slug/<slug>', methods=['GET'])
def get_corporate_content_by_slug(slug):
    """Slug'a göre kurumsal içeriği getir (WP REST API uyumlu)"""
    content = corporate_module.get_by_slug(slug)
    
    if not content:
        return jsonify({'message': 'İçerik bulunamadı!'}), 404
    
    # WP REST API formatına dönüştür
    formatted_content = {
        'id': content.get('id'),
        'title': content.get('title'),
        'content': content.get('content'),
        'slug': content.get('slug'),
        'meta': {
            'description': content.get('meta_description', ''),
            'keywords': content.get('meta_keywords', '')
        },
        'date': content.get('created_at', ''),
        'modified': content.get('updated_at', '')
    }
    
    return jsonify(formatted_content)

# Rapor API Endpoint'leri
@api_bp.route('/reports', methods=['GET'])
def get_reports():
    """Tüm raporları getir (WP REST API uyumlu)"""
    # URL parametrelerini al
    category = request.args.get('category')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Raporları getir
    reports = report_module.get_published_reports(category=category)
    
    # Sayfalama
    total = len(reports)
    start = (page - 1) * per_page
    end = start + per_page
    paged_reports = reports[start:end]
    
    # WP REST API formatına dönüştür
    formatted_reports = []
    for report in paged_reports:
        formatted_reports.append({
            'id': report.get('id'),
            'title': report.get('title'),
            'content': report.get('content'),
            'category': report.get('category'),
            'tags': report.get('tags', '').split(',') if report.get('tags') else [],
            'file_url': report.get('file_url'),
            'view_count': report.get('view_count', 0),
            'date': report.get('created_at', ''),
            'modified': report.get('updated_at', '')
        })
    
    # WP REST API sayfalama başlıklarını ekle
    response = jsonify(formatted_reports)
    response.headers['X-WP-Total'] = total
    response.headers['X-WP-TotalPages'] = (total + per_page - 1) // per_page
    
    return response

@api_bp.route('/reports/<report_id>', methods=['GET'])
def get_report(report_id):
    """Belirli bir raporu getir (WP REST API uyumlu)"""
    report = report_module.get(report_id)
    
    if not report:
        return jsonify({'message': 'Rapor bulunamadı!'}), 404
    
    # Görüntülenme sayısını artır
    report_module.increment_view_count(report_id)
    
    # WP REST API formatına dönüştür
    formatted_report = {
        'id': report.get('id'),
        'title': report.get('title'),
        'content': report.get('content'),
        'category': report.get('category'),
        'tags': report.get('tags', '').split(',') if report.get('tags') else [],
        'file_url': report.get('file_url'),
        'view_count': report.get('view_count', 0) + 1,  # Artırılmış görüntülenme sayısı
        'date': report.get('created_at', ''),
        'modified': report.get('updated_at', '')
    }
    
    return jsonify(formatted_report)

@api_bp.route('/reports/categories', methods=['GET'])
def get_report_categories():
    """Rapor kategorilerini getir (WP REST API uyumlu)"""
    categories = report_module.get_categories()
    
    # WP REST API formatına dönüştür
    formatted_categories = []
    for category in categories:
        formatted_categories.append({
            'name': category,
            'slug': category.lower().replace(' ', '-'),
            'count': report_module.count_by_category(category)
        })
    
    return jsonify(formatted_categories)

# Genel API Endpoint'leri
@api_bp.route('/search', methods=['GET'])
def search():
    """Genel arama endpoint'i (WP REST API uyumlu)"""
    query = request.args.get('q', '')
    if not query:
        return jsonify({'message': 'Arama sorgusu gerekli!'}), 400
    
    results = {
        'team': [],
        'corporate': [],
        'reports': []
    }
    
    # Ekip üyelerinde ara
    team_members = team_module.search(query)
    for member in team_members:
        results['team'].append({
            'id': member.get('id'),
            'name': member.get('name'),
            'position': member.get('position'),
            'type': 'team'
        })
    
    # Kurumsal içerikte ara
    corporate_contents = corporate_module.search(query)
    for content in corporate_contents:
        results['corporate'].append({
            'id': content.get('id'),
            'title': content.get('title'),
            'slug': content.get('slug'),
            'type': 'corporate'
        })
    
    # Raporlarda ara
    reports = report_module.search(query)
    for report in reports:
        results['reports'].append({
            'id': report.get('id'),
            'title': report.get('title'),
            'category': report.get('category'),
            'type': 'report'
        })
    
    return jsonify(results) 