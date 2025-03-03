from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app.modules.page_builder.views import page_builder_bp
from app.models import PageTemplate, PageElement, Corporate
from app.decorators import admin_required, editor_required
from app import db
import uuid
from datetime import datetime
import json

@page_builder_bp.route('/')
@login_required
@admin_required
def index():
    """Sayfa düzenleyici ana sayfa"""
    # Düzenlenebilecek sayfaları getir
    pages_ref = db.collection('corporate').stream()
    pages = [Corporate(**doc.to_dict(), id=doc.id) for doc in pages_ref]
    
    return render_template('page_builder/index.html', pages=pages)

@page_builder_bp.route('/edit/<page_id>', methods=['GET', 'POST'])
@login_required
@editor_required
def edit_page(page_id):
    """Sayfa düzenleme arayüzü"""
    # Sayfa bilgilerini getir
    page_ref = db.collection('corporate').document(page_id).get()
    if not page_ref.exists:
        flash('Sayfa bulunamadı', 'error')
        return redirect(url_for('page_builder.index'))
    
    page = Corporate(**page_ref.to_dict(), id=page_ref.id)
    
    # Sayfa için kullanılan şablonu getir
    template_id = page_ref.to_dict().get('template_id')
    template = None
    
    if template_id:
        template_ref = db.collection('page_templates').document(template_id).get()
        if template_ref.exists:
            template = PageTemplate(**template_ref.to_dict(), id=template_ref.id)
    
    # Tüm şablonları getir
    templates_ref = db.collection('page_templates').stream()
    templates = [PageTemplate(**doc.to_dict(), id=doc.id) for doc in templates_ref]
    
    # Sayfa elemanlarını getir
    elements_ref = db.collection('page_elements').where('page_id', '==', page_id).stream()
    elements = [PageElement(**doc.to_dict(), id=doc.id) for doc in elements_ref]
    
    return render_template(
        'page_builder/editor.html', 
        page=page,
        template=template,
        templates=templates,
        elements=elements
    )

@page_builder_bp.route('/api/elements', methods=['GET'])
@login_required
@editor_required
def get_elements():
    """Sayfa elemanlarını API olarak getir"""
    page_id = request.args.get('page_id')
    if not page_id:
        return jsonify({'error': 'page_id parametresi gerekli'}), 400
    
    elements_ref = db.collection('page_elements').where('page_id', '==', page_id).stream()
    elements = [{"id": doc.id, **doc.to_dict()} for doc in elements_ref]
    
    return jsonify(elements)

@page_builder_bp.route('/api/elements', methods=['POST'])
@login_required
@editor_required
def create_element():
    """Yeni bir sayfa elemanı oluştur"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'JSON veri gönderilmedi'}), 400
    
    # Gerekli alanları kontrol et
    required_fields = ['element_type', 'title', 'content', 'page_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} alanı zorunludur'}), 400
    
    # Yeni eleman oluştur
    element = PageElement(
        element_type=data['element_type'],
        title=data['title'],
        content=data['content'],
        position=data.get('position', {'x': 0, 'y': 0, 'width': 12, 'height': 1}),
        style=data.get('style', {}),
        page_id=data['page_id'],
        id=str(uuid.uuid4()),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Firestore'a kaydet
    db.collection('page_elements').document(element.id).set(element.to_dict())
    
    # Element ID'sini ve oluşturulma bilgisini dön
    response = {
        'id': element.id,
        'created_at': element.created_at.isoformat(),
        'updated_at': element.updated_at.isoformat(),
        **element.to_dict()
    }
    
    return jsonify(response), 201

@page_builder_bp.route('/api/elements/<element_id>', methods=['PUT'])
@login_required
@editor_required
def update_element(element_id):
    """Sayfa elemanını güncelle"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'JSON veri gönderilmedi'}), 400
    
    # Element'in var olduğunu kontrol et
    element_ref = db.collection('page_elements').document(element_id)
    element_doc = element_ref.get()
    
    if not element_doc.exists:
        return jsonify({'error': 'Element bulunamadı'}), 404
    
    # Güncelleme verilerini hazırla
    update_data = {
        'title': data.get('title'),
        'content': data.get('content'),
        'position': data.get('position'),
        'style': data.get('style'),
        'updated_at': datetime.now()
    }
    
    # None olan değerleri kaldır
    update_data = {k: v for k, v in update_data.items() if v is not None}
    
    # Firestore'da güncelle
    element_ref.update(update_data)
    
    return jsonify({'success': True, 'id': element_id})

@page_builder_bp.route('/api/elements/<element_id>', methods=['DELETE'])
@login_required
@editor_required
def delete_element(element_id):
    """Sayfa elemanını sil"""
    # Element'in var olduğunu kontrol et
    element_ref = db.collection('page_elements').document(element_id)
    element_doc = element_ref.get()
    
    if not element_doc.exists:
        return jsonify({'error': 'Element bulunamadı'}), 404
    
    # Firestore'dan sil
    element_ref.delete()
    
    return jsonify({'success': True})

@page_builder_bp.route('/api/pages/<page_id>/template', methods=['PUT'])
@login_required
@editor_required
def set_page_template(page_id):
    """Sayfa için şablon ayarla"""
    data = request.json
    
    if not data or 'template_id' not in data:
        return jsonify({'error': 'template_id parametresi gerekli'}), 400
    
    template_id = data['template_id']
    
    # Sayfa ve şablonun var olduğunu kontrol et
    page_ref = db.collection('corporate').document(page_id)
    page_doc = page_ref.get()
    
    if not page_doc.exists:
        return jsonify({'error': 'Sayfa bulunamadı'}), 404
        
    if template_id:
        template_ref = db.collection('page_templates').document(template_id)
        template_doc = template_ref.get()
        
        if not template_doc.exists:
            return jsonify({'error': 'Şablon bulunamadı'}), 404
    
    # Sayfayı güncelle
    page_ref.update({
        'template_id': template_id,
        'updated_at': datetime.now()
    })
    
    return jsonify({'success': True})

@page_builder_bp.route('/api/pages/<page_id>/save-layout', methods=['POST'])
@login_required
@editor_required
def save_layout(page_id):
    """Sayfa düzenini kaydet"""
    data = request.json
    
    if not data or 'elements' not in data:
        return jsonify({'error': 'elements parametresi gerekli'}), 400
    
    elements = data['elements']
    
    # Batch işlemi başlat
    batch = db.batch()
    
    for element in elements:
        if 'id' not in element:
            continue
            
        element_ref = db.collection('page_elements').document(element['id'])
        
        # Güncelleme verilerini hazırla
        update_data = {
            'position': element.get('position'),
            'updated_at': datetime.now()
        }
        
        # Batch işlemine ekle
        batch.update(element_ref, update_data)
    
    # Batch işlemini uygula
    batch.commit()
    
    return jsonify({'success': True})

@page_builder_bp.route('/element-templates')
@login_required
@editor_required
def element_templates():
    """Eklenebilecek element şablonlarını listele"""
    return render_template('page_builder/element_templates.html') 