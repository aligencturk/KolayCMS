from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.modules.corporate.models import CorporateModule
from app.forms.corporate_form import CorporateForm
from app.utils.validators import validate_slug
from math import ceil

corporate_bp = Blueprint('corporate', __name__, url_prefix='/corporate')
corporate_module = CorporateModule()

@corporate_bp.route('/')
@login_required
def index():
    """Kurumsal içerik listesini görüntüler"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # İçerikleri getir
    contents = corporate_module.list(
        order_by='created_at',
        direction='desc',
        limit=per_page,
        offset=(page-1)*per_page
    )
    
    # Toplam içerik sayısını al
    total_contents = corporate_module.count()
    
    # Sayfalama bilgilerini oluştur
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total_contents,
        'pages': ceil(total_contents / per_page),
        'has_prev': page > 1,
        'has_next': page < ceil(total_contents / per_page),
        'prev_num': page - 1,
        'next_num': page + 1,
        'iter_pages': lambda: range(1, ceil(total_contents / per_page) + 1)
    }
    
    return render_template('corporate/index.html', 
                           contents=contents, 
                           pagination=pagination)

@corporate_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Yeni kurumsal içerik oluşturur"""
    form = CorporateForm()
    
    if form.validate_on_submit():
        try:
            # Slug'ı doğrula
            if not validate_slug(form.slug.data):
                flash('Geçersiz SEO URL formatı. Sadece küçük harf, rakam ve tire kullanabilirsiniz.', 'error')
                return render_template('corporate/form.html', form=form)
            
            # Slug'ın benzersiz olduğunu kontrol et
            existing_content = corporate_module.get_by_slug(form.slug.data)
            if existing_content:
                flash('Bu SEO URL zaten kullanılıyor. Lütfen başka bir URL seçin.', 'error')
                return render_template('corporate/form.html', form=form)
            
            # İçerik oluştur
            content_id = corporate_module.create_content(
                title=form.title.data,
                content=form.content.data,
                slug=form.slug.data,
                meta_description=form.meta_description.data,
                meta_keywords=form.meta_keywords.data,
                is_published=form.is_published.data
            )
            
            if content_id:
                flash('Kurumsal içerik başarıyla oluşturuldu.', 'success')
                return redirect(url_for('corporate.index'))
            else:
                flash('Kurumsal içerik oluşturulurken bir hata oluştu.', 'error')
        except Exception as e:
            flash(f'Bir hata oluştu: {str(e)}', 'error')
    
    return render_template('corporate/form.html', form=form)

@corporate_bp.route('/<content_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(content_id):
    """Kurumsal içerik düzenler"""
    content = corporate_module.get_by_id(content_id)
    
    if not content:
        flash('İçerik bulunamadı.', 'error')
        return redirect(url_for('corporate.index'))
    
    form = CorporateForm(obj=content)
    
    if form.validate_on_submit():
        try:
            # Slug'ı doğrula
            if not validate_slug(form.slug.data):
                flash('Geçersiz SEO URL formatı. Sadece küçük harf, rakam ve tire kullanabilirsiniz.', 'error')
                return render_template('corporate/form.html', form=form, content=content)
            
            # Slug değiştiyse ve yeni slug başka bir içerikte kullanılıyorsa kontrol et
            if form.slug.data != content['slug']:
                existing_content = corporate_module.get_by_slug(form.slug.data)
                if existing_content:
                    flash('Bu SEO URL zaten kullanılıyor. Lütfen başka bir URL seçin.', 'error')
                    return render_template('corporate/form.html', form=form, content=content)
            
            # İçerik güncelle
            update_data = {
                'title': form.title.data,
                'content': form.content.data,
                'slug': form.slug.data,
                'meta_description': form.meta_description.data,
                'meta_keywords': form.meta_keywords.data,
                'is_published': form.is_published.data
            }
            
            if corporate_module.update_content(content_id, update_data):
                flash('Kurumsal içerik başarıyla güncellendi.', 'success')
                return redirect(url_for('corporate.index'))
            else:
                flash('Kurumsal içerik güncellenirken bir hata oluştu.', 'error')
        except Exception as e:
            flash(f'Bir hata oluştu: {str(e)}', 'error')
    
    return render_template('corporate/form.html', form=form, content=content)

@corporate_bp.route('/<content_id>/delete', methods=['DELETE'])
@login_required
def delete(content_id):
    """Kurumsal içerik siler"""
    try:
        if corporate_module.delete(content_id):
            return jsonify({'success': True, 'message': 'İçerik başarıyla silindi.'})
        else:
            return jsonify({'success': False, 'error': 'İçerik silinirken bir hata oluştu.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@corporate_bp.route('/<content_id>/publish', methods=['POST'])
@login_required
def publish(content_id):
    """İçeriği yayınlar"""
    try:
        if corporate_module.publish_content(content_id):
            return jsonify({'success': True, 'message': 'İçerik yayınlandı.'})
        else:
            return jsonify({'success': False, 'error': 'İçerik yayınlanırken bir hata oluştu.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@corporate_bp.route('/<content_id>/unpublish', methods=['POST'])
@login_required
def unpublish(content_id):
    """İçeriği yayından kaldırır"""
    try:
        if corporate_module.unpublish_content(content_id):
            return jsonify({'success': True, 'message': 'İçerik yayından kaldırıldı.'})
        else:
            return jsonify({'success': False, 'error': 'İçerik yayından kaldırılırken bir hata oluştu.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@corporate_bp.route('/<content_id>/view')
@login_required
def view(content_id):
    """İçerik detayını görüntüler"""
    content = corporate_module.get_by_id(content_id)
    
    if not content:
        flash('İçerik bulunamadı.', 'error')
        return redirect(url_for('corporate.index'))
    
    return render_template('corporate/view.html', content=content)
