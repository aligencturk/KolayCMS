from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app.modules.templates.views import templates_bp
from app.models import PageTemplate
from app.decorators import admin_required
from app import db
import uuid
from datetime import datetime

@templates_bp.route('/')
@login_required
@admin_required
def index():
    """Sayfa şablonlarını listele"""
    templates_ref = db.collection('page_templates').stream()
    templates = [PageTemplate(**doc.to_dict(), id=doc.id) for doc in templates_ref]
    return render_template('templates/index.html', templates=templates)

@templates_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    """Yeni şablon oluştur"""
    if request.method == 'POST':
        # Form verilerini al
        name = request.form.get('name')
        description = request.form.get('description')
        template_type = request.form.get('template_type', 'page')
        html_structure = request.form.get('html_structure', '')
        
        # Şablon nesnesi oluştur
        template = PageTemplate(
            name=name,
            description=description,
            template_type=template_type,
            html_structure=html_structure,
            available_slots={
                'header': 'Üst Bölüm',
                'content': 'Ana İçerik',
                'sidebar': 'Kenar Çubuğu',
                'footer': 'Alt Bölüm'
            },
            is_system=False,
            id=str(uuid.uuid4()),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Firestore'a kaydet
        db.collection('page_templates').document(template.id).set(template.to_dict())
        
        flash('Şablon başarıyla oluşturuldu', 'success')
        return redirect(url_for('templates.index'))
        
    return render_template('templates/create.html')

@templates_bp.route('/<template_id>')
@login_required
@admin_required
def view(template_id):
    """Şablon detaylarını görüntüle"""
    template_ref = db.collection('page_templates').document(template_id).get()
    if not template_ref.exists:
        flash('Şablon bulunamadı', 'error')
        return redirect(url_for('templates.index'))
        
    template = PageTemplate(**template_ref.to_dict(), id=template_ref.id)
    return render_template('templates/view.html', template=template)

@templates_bp.route('/<template_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit(template_id):
    """Şablon düzenle"""
    template_ref = db.collection('page_templates').document(template_id).get()
    if not template_ref.exists:
        flash('Şablon bulunamadı', 'error')
        return redirect(url_for('templates.index'))
        
    template_data = template_ref.to_dict()
    
    # Sistem şablonunu düzenlemeyi engelle
    if template_data.get('is_system', False):
        flash('Sistem şablonları düzenlenemez', 'error')
        return redirect(url_for('templates.index'))
    
    if request.method == 'POST':
        # Form verilerini al
        name = request.form.get('name')
        description = request.form.get('description')
        template_type = request.form.get('template_type')
        html_structure = request.form.get('html_structure')
        
        # Slot bilgilerini işle
        available_slots = {}
        slot_keys = request.form.getlist('slot_key')
        slot_names = request.form.getlist('slot_name')
        
        for i in range(len(slot_keys)):
            if slot_keys[i] and slot_names[i]:
                available_slots[slot_keys[i]] = slot_names[i]
        
        # Veritabanını güncelle
        db.collection('page_templates').document(template_id).update({
            'name': name,
            'description': description,
            'template_type': template_type,
            'html_structure': html_structure,
            'available_slots': available_slots,
            'updated_at': datetime.now()
        })
        
        flash('Şablon başarıyla güncellendi', 'success')
        return redirect(url_for('templates.view', template_id=template_id))
        
    template = PageTemplate(**template_data, id=template_id)
    return render_template('templates/edit.html', template=template)

@templates_bp.route('/<template_id>/duplicate', methods=['POST'])
@login_required
@admin_required
def duplicate(template_id):
    """Şablonu kopyala"""
    template_ref = db.collection('page_templates').document(template_id).get()
    if not template_ref.exists:
        flash('Şablon bulunamadı', 'error')
        return redirect(url_for('templates.index'))
        
    template_data = template_ref.to_dict()
    
    # Yeni şablon oluştur
    new_template = PageTemplate(
        name=f"{template_data.get('name')} - Kopya",
        description=template_data.get('description'),
        template_type=template_data.get('template_type'),
        html_structure=template_data.get('html_structure'),
        available_slots=template_data.get('available_slots', {}),
        is_system=False,
        id=str(uuid.uuid4()),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Firestore'a kaydet
    db.collection('page_templates').document(new_template.id).set(new_template.to_dict())
    
    flash('Şablon başarıyla kopyalandı', 'success')
    return redirect(url_for('templates.index'))

@templates_bp.route('/<template_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete(template_id):
    """Şablonu sil"""
    # Sistem şablonunu silmeyi engelle
    template_ref = db.collection('page_templates').document(template_id).get()
    if template_ref.exists and template_ref.to_dict().get('is_system', False):
        flash('Sistem şablonları silinemez', 'error')
        return redirect(url_for('templates.index'))
    
    # Değilse sil
    db.collection('page_templates').document(template_id).delete()
    
    flash('Şablon başarıyla silindi', 'success')
    return redirect(url_for('templates.index')) 