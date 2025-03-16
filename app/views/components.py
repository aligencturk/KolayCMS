from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required
from app import logger
from app.modules.components.models import ComponentModule

components_bp = Blueprint('components', __name__)

@components_bp.route('/components')
@login_required
async def index():
    """Bileşen listesi sayfası"""
    try:
        component_module = ComponentModule()
        components = await component_module.get_all_components()
        
        # Bileşenleri kategorilere göre grupla
        categorized_components = {}
        for component in components:
            category = component['category']
            if category not in categorized_components:
                categorized_components[category] = []
            categorized_components[category].append(component)
        
        return render_template('components/index.html',
                             title='Bileşenler',
                             components=categorized_components)
    except Exception as e:
        logger.error(f"Bileşen listesi yüklenirken hata: {str(e)}", exc_info=True)
        flash('Bileşenler yüklenirken bir hata oluştu.', 'error')
        return render_template('components/index.html',
                             title='Bileşenler',
                             components={})

@components_bp.route('/components/create', methods=['GET', 'POST'])
@login_required
async def create():
    """Yeni bileşen oluşturma"""
    if request.method == 'POST':
        try:
            component_data = {
                'name': request.form['name'],
                'description': request.form.get('description', ''),
                'type': request.form['type'],
                'category': request.form['category'],
                'icon': request.form.get('icon', 'ri-code-line'),
                'html_template': request.form['html_template'],
                'css_styles': request.form.get('css_styles', ''),
                'js_script': request.form.get('js_script', ''),
                'properties': request.form.get('properties', '{}')
            }
            
            # JSON string'i dict'e çevir
            import json
            try:
                component_data['properties'] = json.loads(component_data['properties'])
            except:
                component_data['properties'] = {}
            
            component_module = ComponentModule()
            if await component_module.create_component(component_data):
                flash('Bileşen başarıyla oluşturuldu.', 'success')
                return redirect(url_for('components.index'))
            else:
                flash('Bileşen oluşturulurken bir hata oluştu.', 'error')
        except Exception as e:
            logger.error(f"Bileşen oluşturma hatası: {str(e)}", exc_info=True)
            flash('Bileşen oluşturulurken bir hata oluştu.', 'error')
    
    return render_template('components/create.html',
                         title='Yeni Bileşen')

@components_bp.route('/components/<component_id>/edit', methods=['GET', 'POST'])
@login_required
async def edit(component_id):
    """Bileşen düzenleme"""
    component_module = ComponentModule()
    
    if request.method == 'POST':
        try:
            component_data = {
                'name': request.form['name'],
                'description': request.form.get('description', ''),
                'type': request.form['type'],
                'category': request.form['category'],
                'icon': request.form.get('icon', 'ri-code-line'),
                'html_template': request.form['html_template'],
                'css_styles': request.form.get('css_styles', ''),
                'js_script': request.form.get('js_script', ''),
                'properties': request.form.get('properties', '{}')
            }
            
            # JSON string'i dict'e çevir
            import json
            try:
                component_data['properties'] = json.loads(component_data['properties'])
            except:
                component_data['properties'] = {}
            
            if await component_module.update_component(component_id, component_data):
                flash('Bileşen başarıyla güncellendi.', 'success')
                return redirect(url_for('components.index'))
            else:
                flash('Bileşen güncellenirken bir hata oluştu.', 'error')
        except Exception as e:
            logger.error(f"Bileşen güncelleme hatası: {str(e)}", exc_info=True)
            flash('Bileşen güncellenirken bir hata oluştu.', 'error')
    
    component = await component_module.get_component(component_id)
    if not component:
        flash('Bileşen bulunamadı.', 'error')
        return redirect(url_for('components.index'))
    
    return render_template('components/edit.html',
                         title='Bileşen Düzenle',
                         component=component)

@components_bp.route('/components/<component_id>/delete', methods=['POST'])
@login_required
async def delete(component_id):
    """Bileşen silme"""
    try:
        component_module = ComponentModule()
        if await component_module.delete_component(component_id):
            flash('Bileşen başarıyla silindi.', 'success')
        else:
            flash('Bileşen silinirken bir hata oluştu.', 'error')
    except Exception as e:
        logger.error(f"Bileşen silme hatası: {str(e)}", exc_info=True)
        flash('Bileşen silinirken bir hata oluştu.', 'error')
    
    return redirect(url_for('components.index'))

@components_bp.route('/components/<component_id>/preview', methods=['POST'])
@login_required
async def preview(component_id):
    """Bileşen önizleme"""
    try:
        properties = request.get_json()
        
        component_module = ComponentModule()
        result = await component_module.render_component(component_id, properties)
        
        if result:
            return jsonify({
                'success': True,
                'html': result['html'],
                'css': result['css'],
                'js': result['js']
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Bileşen render edilemedi.'
            })
    except Exception as e:
        logger.error(f"Bileşen önizleme hatası: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Bileşen önizleme hatası oluştu.'
        }) 