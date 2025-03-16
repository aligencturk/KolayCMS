from flask import render_template, redirect, url_for, request, current_app, abort
from app.modules.website.views import website_bp
from app import db
from app.models import Corporate, PageElement, PageTemplate, Component, Slider, Service, TeamMember, Project

@website_bp.route('/')
def home():
    """Ana sayfa görüntüleme"""
    # Ana sayfa bilgilerini getir (Corporate tablosunda 'home' olarak işaretlenmiş sayfa)
    home_page_ref = db.collection('corporate').where('slug', '==', 'home').limit(1).stream()
    home_page = None
    
    for doc in home_page_ref:
        home_page = Corporate(**doc.to_dict(), id=doc.id)
        break
    
    if not home_page:
        # Ana sayfa bulunamadıysa varsayılan içerikle göster
        return render_template('website/home.html', page_title="Ana Sayfa", elements=[])
    
    # Ana sayfa elementlerini getir
    elements_ref = db.collection('page_elements').where('page_id', '==', home_page.id).stream()
    elements = [PageElement(**doc.to_dict(), id=doc.id) for doc in elements_ref]
    
    # Slider, hizmetler, ekip ve projeler gibi dinamik içerikleri getir
    sliders = get_active_sliders()
    services = get_featured_services()
    team_members = get_featured_team_members()
    projects = get_featured_projects()
    
    # Şablon bilgilerini getir
    template = None
    if home_page.template_id:
        template_ref = db.collection('page_templates').document(home_page.template_id).get()
        if template_ref.exists:
            template = PageTemplate(**template_ref.to_dict(), id=template_ref.id)
    
    # Website adresini hesapla
    website_url = current_app.config.get('WEBSITE_URL', request.host_url)
    
    return render_template(
        'website/home.html',
        page=home_page,
        elements=elements,
        template=template,
        sliders=sliders,
        services=services,
        team_members=team_members,
        projects=projects,
        website_url=website_url
    )

@website_bp.route('/<slug>')
def page(slug):
    """Belirtilen sayfa slug'ına göre sayfa görüntüleme"""
    # Sayfa bilgilerini getir
    page_ref = db.collection('corporate').where('slug', '==', slug).limit(1).stream()
    page_obj = None
    
    for doc in page_ref:
        page_obj = Corporate(**doc.to_dict(), id=doc.id)
        break
    
    if not page_obj:
        abort(404)  # Sayfa bulunamadı
    
    # Sayfa elementlerini getir
    elements_ref = db.collection('page_elements').where('page_id', '==', page_obj.id).stream()
    elements = [PageElement(**doc.to_dict(), id=doc.id) for doc in elements_ref]
    
    # Şablon bilgilerini getir
    template = None
    if page_obj.template_id:
        template_ref = db.collection('page_templates').document(page_obj.template_id).get()
        if template_ref.exists:
            template = PageTemplate(**template_ref.to_dict(), id=template_ref.id)
    
    # Website adresini hesapla
    website_url = current_app.config.get('WEBSITE_URL', request.host_url)
    
    return render_template(
        f'website/{slug}.html' if template is None else template.template_path,
        page=page_obj,
        elements=elements,
        template=template,
        website_url=website_url
    )

# Yardımcı fonksiyonlar
def get_active_sliders():
    """Aktif sliderları getir"""
    sliders_ref = db.collection('sliders').where('is_active', '==', True).stream()
    return [Slider(**doc.to_dict(), id=doc.id) for doc in sliders_ref]

def get_featured_services():
    """Öne çıkarılmış hizmetleri getir"""
    services_ref = db.collection('services').where('is_featured', '==', True).where('is_active', '==', True).stream()
    return [Service(**doc.to_dict(), id=doc.id) for doc in services_ref]

def get_featured_team_members():
    """Öne çıkarılmış ekip üyelerini getir"""
    team_ref = db.collection('team_members').where('is_featured', '==', True).where('is_active', '==', True).stream()
    return [TeamMember(**doc.to_dict(), id=doc.id) for doc in team_ref]

def get_featured_projects():
    """Öne çıkarılmış projeleri getir"""
    projects_ref = db.collection('projects').where('is_featured', '==', True).where('is_active', '==', True).stream()
    return [Project(**doc.to_dict(), id=doc.id) for doc in projects_ref] 