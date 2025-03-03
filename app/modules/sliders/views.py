from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.modules.sliders.models import SliderModule
from app.forms.slider_form import SliderForm
from app.utils.validators import validate_image_url
from math import ceil

sliders_bp = Blueprint('sliders', __name__, url_prefix='/sliders')
slider_module = SliderModule()

@sliders_bp.route('/')
@login_required
def index():
    """Slider listesini görüntüler"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Slider'ları getir
    sliders = slider_module.list(
        order_by='order',
        direction='asc',
        limit=per_page,
        offset=(page-1)*per_page
    )
    
    # Toplam slider sayısını al
    total_sliders = slider_module.count()
    
    # Sayfalama bilgilerini oluştur
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total_sliders,
        'pages': ceil(total_sliders / per_page),
        'has_prev': page > 1,
        'has_next': page < ceil(total_sliders / per_page),
        'prev_num': page - 1,
        'next_num': page + 1,
        'iter_pages': lambda: range(1, ceil(total_sliders / per_page) + 1)
    }
    
    return render_template('sliders/index.html', 
                           sliders=sliders, 
                           pagination=pagination)

@sliders_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Yeni slider oluşturur"""
    form = SliderForm()
    
    if form.validate_on_submit():
        try:
            # Görsel URL'sini doğrula
            if not validate_image_url(form.image_url.data):
                flash('Geçersiz görsel URL formatı. Desteklenen formatlar: jpg, jpeg, png, gif, webp', 'error')
                return render_template('sliders/form.html', form=form)
            
            # Slider oluştur
            slider_id = slider_module.create_slider(
                title=form.title.data,
                image_url=form.image_url.data,
                description=form.description.data,
                link=form.link.data,
                order=form.order.data,
                is_active=form.is_active.data
            )
            
            if slider_id:
                flash('Slider başarıyla oluşturuldu.', 'success')
                return redirect(url_for('sliders.index'))
            else:
                flash('Slider oluşturulurken bir hata oluştu.', 'error')
        except Exception as e:
            flash(f'Bir hata oluştu: {str(e)}', 'error')
    
    return render_template('sliders/form.html', form=form)

@sliders_bp.route('/<slider_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(slider_id):
    """Slider düzenler"""
    slider = slider_module.get_by_id(slider_id)
    
    if not slider:
        flash('Slider bulunamadı.', 'error')
        return redirect(url_for('sliders.index'))
    
    form = SliderForm(obj=slider)
    
    if form.validate_on_submit():
        try:
            # Görsel URL'sini doğrula
            if not validate_image_url(form.image_url.data):
                flash('Geçersiz görsel URL formatı. Desteklenen formatlar: jpg, jpeg, png, gif, webp', 'error')
                return render_template('sliders/form.html', form=form, slider=slider)
            
            # Slider güncelle
            update_data = {
                'title': form.title.data,
                'image_url': form.image_url.data,
                'description': form.description.data,
                'link': form.link.data,
                'order': form.order.data,
                'is_active': form.is_active.data
            }
            
            if slider_module.update_slider(slider_id, update_data):
                flash('Slider başarıyla güncellendi.', 'success')
                return redirect(url_for('sliders.index'))
            else:
                flash('Slider güncellenirken bir hata oluştu.', 'error')
        except Exception as e:
            flash(f'Bir hata oluştu: {str(e)}', 'error')
    
    return render_template('sliders/form.html', form=form, slider=slider)

@sliders_bp.route('/<slider_id>/delete', methods=['DELETE'])
@login_required
def delete(slider_id):
    """Slider siler"""
    try:
        if slider_module.delete(slider_id):
            return jsonify({'success': True, 'message': 'Slider başarıyla silindi.'})
        else:
            return jsonify({'success': False, 'error': 'Slider silinirken bir hata oluştu.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sliders_bp.route('/<slider_id>/activate', methods=['POST'])
@login_required
def activate(slider_id):
    """Slider'ı aktifleştirir"""
    try:
        if slider_module.activate_slider(slider_id):
            return jsonify({'success': True, 'message': 'Slider aktifleştirildi.'})
        else:
            return jsonify({'success': False, 'error': 'Slider aktifleştirilirken bir hata oluştu.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sliders_bp.route('/<slider_id>/deactivate', methods=['POST'])
@login_required
def deactivate(slider_id):
    """Slider'ı deaktifleştirir"""
    try:
        if slider_module.deactivate_slider(slider_id):
            return jsonify({'success': True, 'message': 'Slider deaktifleştirildi.'})
        else:
            return jsonify({'success': False, 'error': 'Slider deaktifleştirilirken bir hata oluştu.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@sliders_bp.route('/reorder', methods=['POST'])
@login_required
def reorder():
    """Slider'ların sırasını günceller"""
    try:
        order_data = request.json.get('order_data', [])
        
        if not order_data:
            return jsonify({'success': False, 'error': 'Sıralama verisi bulunamadı.'}), 400
        
        if slider_module.reorder_sliders(order_data):
            return jsonify({'success': True, 'message': 'Slider sıralaması güncellendi.'})
        else:
            return jsonify({'success': False, 'error': 'Slider sıralaması güncellenirken bir hata oluştu.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
