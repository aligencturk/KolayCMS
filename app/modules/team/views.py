from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from app.modules.team.models import TeamModule
from app.forms.team_form import TeamMemberForm
from app.utils.validators import validate_image_url
from math import ceil

team_bp = Blueprint('team', __name__, url_prefix='/team')
team_module = TeamModule()

@team_bp.route('/')
@login_required
def index():
    """Ekip üyeleri listesini görüntüler"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Ekip üyelerini getir
    members = team_module.list(
        order_by='order',
        direction='asc',
        limit=per_page,
        offset=(page-1)*per_page
    )
    
    # Toplam ekip üyesi sayısını al
    total_members = team_module.count()
    
    # Sayfalama bilgilerini oluştur
    pagination = {
        'page': page,
        'per_page': per_page,
        'total': total_members,
        'pages': ceil(total_members / per_page),
        'has_prev': page > 1,
        'has_next': page < ceil(total_members / per_page),
        'prev_num': page - 1,
        'next_num': page + 1,
        'iter_pages': lambda: range(1, ceil(total_members / per_page) + 1)
    }
    
    return render_template('team/index.html', 
                           members=members, 
                           pagination=pagination)

@team_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Yeni ekip üyesi oluşturur"""
    form = TeamMemberForm()
    
    if form.validate_on_submit():
        try:
            # Fotoğraf URL'sini doğrula (eğer varsa)
            if form.photo_url.data and not validate_image_url(form.photo_url.data):
                flash('Geçersiz fotoğraf URL formatı. Desteklenen formatlar: jpg, jpeg, png, gif, webp', 'error')
                return render_template('team/form.html', form=form)
            
            # Sosyal medya bilgilerini topla
            social_media = {}
            if form.facebook.data:
                social_media['facebook'] = form.facebook.data
            if form.twitter.data:
                social_media['twitter'] = form.twitter.data
            if form.instagram.data:
                social_media['instagram'] = form.instagram.data
            if form.linkedin.data:
                social_media['linkedin'] = form.linkedin.data
            
            # Ekip üyesi oluştur
            member_id = team_module.create_member(
                name=form.name.data,
                position=form.position.data,
                photo_url=form.photo_url.data,
                bio=form.bio.data,
                email=form.email.data,
                phone=form.phone.data,
                social_media=social_media,
                order=form.order.data,
                is_active=form.is_active.data
            )
            
            if member_id:
                flash('Ekip üyesi başarıyla oluşturuldu.', 'success')
                return redirect(url_for('team.index'))
            else:
                flash('Ekip üyesi oluşturulurken bir hata oluştu.', 'error')
        except Exception as e:
            flash(f'Bir hata oluştu: {str(e)}', 'error')
    
    return render_template('team/form.html', form=form)

@team_bp.route('/<member_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(member_id):
    """Ekip üyesi düzenler"""
    member = team_module.get_by_id(member_id)
    
    if not member:
        flash('Ekip üyesi bulunamadı.', 'error')
        return redirect(url_for('team.index'))
    
    form = TeamMemberForm(obj=member)
    
    # Sosyal medya alanlarını doldur
    if member.get('social_media'):
        form.facebook.data = member['social_media'].get('facebook', '')
        form.twitter.data = member['social_media'].get('twitter', '')
        form.instagram.data = member['social_media'].get('instagram', '')
        form.linkedin.data = member['social_media'].get('linkedin', '')
    
    if form.validate_on_submit():
        try:
            # Fotoğraf URL'sini doğrula (eğer varsa)
            if form.photo_url.data and not validate_image_url(form.photo_url.data):
                flash('Geçersiz fotoğraf URL formatı. Desteklenen formatlar: jpg, jpeg, png, gif, webp', 'error')
                return render_template('team/form.html', form=form, member=member)
            
            # Sosyal medya bilgilerini topla
            social_media = {}
            if form.facebook.data:
                social_media['facebook'] = form.facebook.data
            if form.twitter.data:
                social_media['twitter'] = form.twitter.data
            if form.instagram.data:
                social_media['instagram'] = form.instagram.data
            if form.linkedin.data:
                social_media['linkedin'] = form.linkedin.data
            
            # Ekip üyesi güncelle
            update_data = {
                'name': form.name.data,
                'position': form.position.data,
                'photo_url': form.photo_url.data,
                'bio': form.bio.data,
                'email': form.email.data,
                'phone': form.phone.data,
                'social_media': social_media,
                'order': form.order.data,
                'is_active': form.is_active.data
            }
            
            if team_module.update_member(member_id, update_data):
                flash('Ekip üyesi başarıyla güncellendi.', 'success')
                return redirect(url_for('team.index'))
            else:
                flash('Ekip üyesi güncellenirken bir hata oluştu.', 'error')
        except Exception as e:
            flash(f'Bir hata oluştu: {str(e)}', 'error')
    
    return render_template('team/form.html', form=form, member=member)

@team_bp.route('/<member_id>/delete', methods=['DELETE'])
@login_required
def delete(member_id):
    """Ekip üyesi siler"""
    try:
        if team_module.delete(member_id):
            return jsonify({'success': True, 'message': 'Ekip üyesi başarıyla silindi.'})
        else:
            return jsonify({'success': False, 'error': 'Ekip üyesi silinirken bir hata oluştu.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@team_bp.route('/<member_id>/activate', methods=['POST'])
@login_required
def activate(member_id):
    """Ekip üyesini aktifleştirir"""
    try:
        if team_module.activate_member(member_id):
            return jsonify({'success': True, 'message': 'Ekip üyesi aktifleştirildi.'})
        else:
            return jsonify({'success': False, 'error': 'Ekip üyesi aktifleştirilirken bir hata oluştu.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@team_bp.route('/<member_id>/deactivate', methods=['POST'])
@login_required
def deactivate(member_id):
    """Ekip üyesini deaktifleştirir"""
    try:
        if team_module.deactivate_member(member_id):
            return jsonify({'success': True, 'message': 'Ekip üyesi deaktifleştirildi.'})
        else:
            return jsonify({'success': False, 'error': 'Ekip üyesi deaktifleştirilirken bir hata oluştu.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@team_bp.route('/reorder', methods=['POST'])
@login_required
def reorder():
    """Ekip üyelerinin sırasını günceller"""
    try:
        order_data = request.json.get('order_data', [])
        
        if not order_data:
            return jsonify({'success': False, 'error': 'Sıralama verisi bulunamadı.'}), 400
        
        if team_module.reorder_members(order_data):
            return jsonify({'success': True, 'message': 'Ekip üyeleri sıralaması güncellendi.'})
        else:
            return jsonify({'success': False, 'error': 'Ekip üyeleri sıralaması güncellenirken bir hata oluştu.'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@team_bp.route('/view/<member_id>')
@login_required
def view(member_id):
    """Ekip üyesi detaylarını görüntüle"""
    member = team_module.get_member(member_id)
    if not member:
        flash('Ekip üyesi bulunamadı.', 'error')
        return redirect(url_for('team.index'))
    
    return render_template('team/view.html', member=member)
