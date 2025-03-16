from flask import Blueprint, render_template, redirect, url_for, request, current_app, flash, jsonify
from flask_login import current_user, login_required
from app import db, logger
from app.modules.reports.models import ReportModule
from app.modules.sliders.models import SliderModule
from app.modules.corporate.models import CorporateModule
from app.modules.team.models import TeamModule
from app.modules.themes.models import ThemeModule
import asyncio
import socket
from datetime import datetime
from google.cloud import storage
from google.cloud import firestore
import firebase_admin
import os
import json
import tempfile
import shutil
import patoolib

def find_free_port(start_port=5000, max_port=5100):
    """Kullanılabilir bir port bul"""
    for port in range(start_port, max_port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('', port))
                return port
        except OSError:
            continue
    return None

# Kullanılabilir port bul
PORT = find_free_port()
if PORT is None:
    logger.error("Kullanılabilir port bulunamadı!")
    raise RuntimeError("Kullanılabilir port bulunamadı!")

# Blueprint tanımı
main_bp = Blueprint('main', __name__)

# Modülleri başlat
modules = {}
try:
    logger.debug("Modüller başlatılıyor...")
    modules['report'] = ReportModule()
    modules['slider'] = SliderModule()
    modules['corporate'] = CorporateModule()
    modules['team'] = TeamModule()
    logger.debug("Modüller başarıyla başlatıldı")
except Exception as e:
    logger.error(f"Modüller başlatılırken hata: {str(e)}", exc_info=True)

@main_bp.route('/')
def index():
    """Ana sayfa"""
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.dashboard'))
        return redirect(url_for('auth.login'))
    except Exception as e:
        logger.error(f"Ana sayfa yönlendirmesinde hata: {str(e)}", exc_info=True)
        return render_template('errors/500.html'), 500

@main_bp.route('/dashboard')
@login_required
async def dashboard():
    """Dashboard sayfası"""
    logger.debug("Dashboard sayfası yükleniyor...")
    
    # Varsayılan değerleri tanımla
    counts = {
        'report_count': 0,
        'slider_count': 0,
        'corporate_count': 0,
        'team_count': 0
    }
    
    try:
        # Her modül için ayrı try-except blokları
        if 'report' in modules:
            try:
                logger.debug("Rapor sayısı hesaplanıyor...")
                reports = await modules['report'].get_all_reports()
                counts['report_count'] = len(reports) if reports else 0
                logger.debug(f"Rapor sayısı: {counts['report_count']}")
            except Exception as e:
                logger.error(f"Rapor sayısı hesaplanırken hata: {str(e)}", exc_info=True)
            
        if 'slider' in modules:
            try:
                logger.debug("Slider sayısı hesaplanıyor...")
                sliders = await modules['slider'].get_all_sliders()
                counts['slider_count'] = len(sliders) if sliders else 0
                logger.debug(f"Slider sayısı: {counts['slider_count']}")
            except Exception as e:
                logger.error(f"Slider sayısı hesaplanırken hata: {str(e)}", exc_info=True)
            
        if 'corporate' in modules:
            try:
                logger.debug("Kurumsal içerik sayısı hesaplanıyor...")
                contents = await modules['corporate'].get_all_contents()
                counts['corporate_count'] = len(contents) if contents else 0
                logger.debug(f"Kurumsal içerik sayısı: {counts['corporate_count']}")
            except Exception as e:
                logger.error(f"Kurumsal içerik sayısı hesaplanırken hata: {str(e)}", exc_info=True)
            
        if 'team' in modules:
            try:
                logger.debug("Ekip üyesi sayısı hesaplanıyor...")
                members = await modules['team'].get_active_members()
                counts['team_count'] = len(members) if members else 0
                logger.debug(f"Ekip üyesi sayısı: {counts['team_count']}")
            except Exception as e:
                logger.error(f"Ekip üyesi sayısı hesaplanırken hata: {str(e)}", exc_info=True)
        
        logger.debug("Dashboard template render ediliyor...")
        return render_template('dashboard.html', 
                             title='Dashboard',
                             now=datetime.now(),
                             **counts)
                             
    except Exception as e:
        # Genel bir hata durumunda varsayılan değerlerle devam et
        logger.error(f"Dashboard yüklenirken genel hata: {str(e)}", exc_info=True)
        return render_template('dashboard.html', 
                             title='Dashboard',
                             now=datetime.now(),
                             **counts)

@main_bp.route('/profile')
@login_required
def profile():
    """Kullanıcı profil sayfası"""
    try:
        return render_template('profile.html', title='Profilim')
    except Exception as e:
        logger.error(f"Profil sayfası yüklenirken hata: {str(e)}", exc_info=True)
        return render_template('errors/500.html'), 500

@main_bp.route('/templates/create', methods=['GET', 'POST'])
@login_required
async def create_template():
    if request.method == 'POST':
        try:
            template_name = request.form.get('template_name')
            description = request.form.get('description')
            template_type = request.form.get('template_type')
            html_content = request.form.get('html_content')
            
            # Dosya yükleme işlemi
            preview_image = request.files.get('preview_image')
            preview_url = None
            
            if preview_image:
                # Firebase Storage'a yükle
                bucket = storage.bucket(app=firebase_admin.get_app())
                blob = bucket.blob(f'templates/previews/{template_name}_{preview_image.filename}')
                blob.upload_from_string(
                    preview_image.read(),
                    content_type=preview_image.content_type
                )
                preview_url = blob.public_url

            # Template verilerini Firestore'a kaydet
            template_ref = db.collection('templates').document()
            await template_ref.set({
                'name': template_name,
                'description': description,
                'type': template_type,
                'html_content': html_content,
                'preview_url': preview_url,
                'created_at': firestore.SERVER_TIMESTAMP,
                'created_by': current_user.uid
            })

            flash('Şablon başarıyla oluşturuldu.', 'success')
            return redirect(url_for('main.templates'))
            
        except Exception as e:
            logger.error(f"Şablon oluşturma hatası: {str(e)}", exc_info=True)
            flash('Şablon oluşturulurken bir hata oluştu.', 'error')
            
    return render_template('templates/create.html',
                         title='Yeni Şablon')

@main_bp.route('/templates')
@login_required
async def templates():
    try:
        # Şablonları Firestore'dan çek
        templates_ref = db.collection('templates')
        templates_docs = await templates_ref.get()
        
        templates_list = []
        for doc in templates_docs:
            template_data = doc.to_dict()
            template_data['id'] = doc.id
            templates_list.append(template_data)
            
        return render_template('templates/list.html',
                             title='Şablonlar',
                             templates=templates_list)
                             
    except Exception as e:
        logger.error(f"Şablonları listelerken hata: {str(e)}", exc_info=True)
        flash('Şablonlar yüklenirken bir hata oluştu.', 'error')
        return render_template('templates/list.html',
                             title='Şablonlar',
                             templates=[])

@main_bp.route('/templates/<template_id>/edit', methods=['GET', 'POST'])
@login_required
async def edit_template(template_id):
    try:
        template_ref = db.collection('templates').document(template_id)
        template_doc = await template_ref.get()
        
        if not template_doc.exists:
            flash('Şablon bulunamadı.', 'error')
            return redirect(url_for('main.templates'))
            
        template_data = template_doc.to_dict()
        
        if request.method == 'POST':
            # Form verilerini al
            template_name = request.form.get('template_name')
            description = request.form.get('description')
            template_type = request.form.get('template_type')
            html_content = request.form.get('html_content')
            
            # Dosya yükleme işlemi
            preview_image = request.files.get('preview_image')
            preview_url = template_data.get('preview_url')
            
            if preview_image:
                # Eski resmi sil
                if preview_url:
                    try:
                        old_blob = storage.bucket().blob(preview_url.split('/')[-1])
                        old_blob.delete()
                    except Exception as e:
                        logger.warning(f"Eski önizleme resmi silinirken hata: {str(e)}")
                
                # Yeni resmi yükle
                bucket = storage.bucket(app=firebase_admin.get_app())
                blob = bucket.blob(f'templates/previews/{template_name}_{preview_image.filename}')
                blob.upload_from_string(
                    preview_image.read(),
                    content_type=preview_image.content_type
                )
                preview_url = blob.public_url
            
            # Template'i güncelle
            await template_ref.update({
                'name': template_name,
                'description': description,
                'type': template_type,
                'html_content': html_content,
                'preview_url': preview_url,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'updated_by': current_user.uid
            })
            
            flash('Şablon başarıyla güncellendi.', 'success')
            return redirect(url_for('main.templates'))
            
        return render_template('templates/edit.html',
                             title='Şablon Düzenle',
                             template=template_data)
                             
    except Exception as e:
        logger.error(f"Şablon düzenleme hatası: {str(e)}", exc_info=True)
        flash('Şablon düzenlenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.templates'))

@main_bp.route('/templates/<template_id>/delete', methods=['POST'])
@login_required
async def delete_template(template_id):
    try:
        template_ref = db.collection('templates').document(template_id)
        template_doc = await template_ref.get()
        
        if not template_doc.exists:
            flash('Şablon bulunamadı.', 'error')
            return redirect(url_for('main.templates'))
            
        template_data = template_doc.to_dict()
        
        # Önizleme resmini sil
        if template_data.get('preview_url'):
            try:
                blob = storage.bucket().blob(template_data['preview_url'].split('/')[-1])
                blob.delete()
            except Exception as e:
                logger.warning(f"Önizleme resmi silinirken hata: {str(e)}")
        
        # Template'i sil
        await template_ref.delete()
        
        flash('Şablon başarıyla silindi.', 'success')
        return redirect(url_for('main.templates'))
        
    except Exception as e:
        logger.error(f"Şablon silme hatası: {str(e)}", exc_info=True)
        flash('Şablon silinirken bir hata oluştu.', 'error')
        return redirect(url_for('main.templates'))

@main_bp.route('/page-builder')
@login_required
async def page_builder():
    """Sayfa düzenleyici ana sayfası"""
    try:
        # Aktif temayı al
        theme_module = ThemeModule()
        active_theme = await theme_module.get_active_theme()
        
        if not active_theme:
            flash('Aktif tema bulunamadı. Lütfen önce bir tema aktifleştirin.', 'warning')
            return redirect(url_for('main.list_themes'))
        
        # Temanın sayfalarını al
        pages = await theme_module.get_theme_pages(active_theme['id'])
        
        return render_template('page_builder/index.html',
                             title='Sayfa Düzenleyici',
                             theme=active_theme,
                             pages=pages)
                             
    except Exception as e:
        logger.error(f"Sayfa düzenleyici yüklenirken hata: {str(e)}", exc_info=True)
        flash('Sayfa düzenleyici yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/page-builder/<page_id>')
@login_required
async def edit_page(page_id):
    """Sayfa düzenleme ekranı"""
    try:
        # Aktif temayı al
        theme_module = ThemeModule()
        active_theme = await theme_module.get_active_theme()
        
        if not active_theme:
            flash('Aktif tema bulunamadı. Lütfen önce bir tema aktifleştirin.', 'warning')
            return redirect(url_for('main.list_themes'))
        
        # Sayfayı al
        page = await theme_module.get_page(page_id)
        if not page:
            flash('Sayfa bulunamadı.', 'error')
            return redirect(url_for('main.page_builder'))
        
        # Bileşenleri al
        from app.modules.components.models import ComponentModule
        component_module = ComponentModule()
        components = await component_module.get_all_components()
        
        # Bileşenleri kategorilere göre grupla
        categorized_components = {}
        for component in components:
            category = component['category']
            if category not in categorized_components:
                categorized_components[category] = []
            categorized_components[category].append(component)
        
        return render_template('page_builder/editor.html',
                             title=f'Sayfa Düzenle: {page["title"]}',
                             theme=active_theme,
                             page=page,
                             components=categorized_components)
                             
    except Exception as e:
        logger.error(f"Sayfa düzenleme ekranı yüklenirken hata: {str(e)}", exc_info=True)
        flash('Sayfa düzenleme ekranı yüklenirken bir hata oluştu.', 'error')
        return redirect(url_for('main.page_builder'))

@main_bp.route('/page-builder/<page_id>/save', methods=['POST'])
@login_required
async def save_page(page_id):
    """Sayfa düzenlemelerini kaydet"""
    try:
        data = request.get_json()
        components = data.get('components', [])
        
        # Bileşenleri render et
        from app.modules.components.models import ComponentModule
        component_module = ComponentModule()
        
        rendered_content = []
        for component in components:
            result = await component_module.render_component(
                component['id'],
                component.get('properties', {})
            )
            if result:
                rendered_content.append(result)
        
        # Sayfa içeriğini oluştur
        html_content = '\n'.join(item['html'] for item in rendered_content)
        css_content = '\n'.join(item['css'] for item in rendered_content if item.get('css'))
        js_content = '\n'.join(item['js'] for item in rendered_content if item.get('js'))
        
        # Sayfayı güncelle
        theme_module = ThemeModule()
        result = await theme_module.update_page(page_id, {
            'content': html_content,
            'styles': css_content,
            'scripts': js_content,
            'components': components  # Bileşen verilerini de sakla
        })
        
        if result:
            return jsonify({
                'success': True,
                'message': 'Sayfa başarıyla kaydedildi.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Sayfa kaydedilirken bir hata oluştu.'
            })
            
    except Exception as e:
        logger.error(f"Sayfa kaydedilirken hata: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': 'Sayfa kaydedilirken bir hata oluştu.'
        })

@main_bp.route('/page-builder/preview/<page_id>')
@login_required
def preview_page_layout(page_id):
    try:
        # Sayfayı Firestore'dan al
        page_ref = db.collection('pages').document(page_id)
        page = page_ref.get()
        
        if not page.exists:
            flash('Sayfa bulunamadı', 'error')
            return redirect(url_for('main.page_builder'))
        
        page_data = page.to_dict()
        return render_template('page_builder/preview.html', 
                             layout=page_data.get('layout'),
                             title=page_data.get('title'))
                             
    except Exception as e:
        flash(f'Sayfa önizleme hatası: {str(e)}', 'error')
        return redirect(url_for('main.page_builder'))

@main_bp.route('/page-builder/save', methods=['POST'])
@login_required
def save_page_layout():
    try:
        data = request.get_json()
        page_id = data.get('page_id')
        layout = data.get('layout')
        title = data.get('title', 'Yeni Sayfa')
        
        # Sayfa verilerini Firestore'a kaydet
        if page_id:
            # Mevcut sayfayı güncelle
            page_ref = db.collection('pages').document(page_id)
            page_ref.update({
                'layout': layout,
                'title': title,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'updated_by': current_user.email,
                'styles': {
                    component['type']: component.get('styles', {})
                    for component in layout['components']
                }
            })
        else:
            # Yeni sayfa oluştur
            page_ref = db.collection('pages').add({
                'layout': layout,
                'title': title,
                'created_at': firestore.SERVER_TIMESTAMP,
                'created_by': current_user.email,
                'updated_at': firestore.SERVER_TIMESTAMP,
                'updated_by': current_user.email,
                'styles': {
                    component['type']: component.get('styles', {})
                    for component in layout['components']
                }
            })
            page_id = page_ref[1].id
        
        return jsonify({
            'success': True,
            'page_id': page_id,
            'message': 'Sayfa başarıyla kaydedildi'
        })
        
    except Exception as e:
        logger.error(f"Sayfa kaydedilirken hata: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Sayfa kaydedilirken hata oluştu: {str(e)}'
        }), 500

@main_bp.route('/page-builder/load/<page_id>')
@login_required
def load_page(page_id):
    try:
        # Sayfayı Firestore'dan al
        page_ref = db.collection('pages').document(page_id)
        page = page_ref.get()
        
        if not page.exists:
            return jsonify({
                'success': False,
                'message': 'Sayfa bulunamadı'
            }), 404
        
        page_data = page.to_dict()
        return jsonify({
            'success': True,
            'page': {
                'id': page_id,
                'title': page_data.get('title'),
                'layout': page_data.get('layout')
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Sayfa yüklenirken hata oluştu: {str(e)}'
        }), 500

@main_bp.route('/page-builder/delete/<page_id>', methods=['DELETE'])
@login_required
def delete_page(page_id):
    try:
        # Sayfayı Firestore'dan sil
        page_ref = db.collection('pages').document(page_id)
        page = page_ref.get()
        
        if not page.exists:
            return jsonify({
                'success': False,
                'message': 'Sayfa bulunamadı'
            }), 404
        
        page_ref.delete()
        return jsonify({
            'success': True,
            'message': 'Sayfa başarıyla silindi'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Sayfa silinirken hata oluştu: {str(e)}'
        }), 500

@main_bp.app_errorhandler(404)
def page_not_found(e):
    """404 hata sayfası"""
    logger.warning(f"404 hatası: {request.url}")
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(500)
def internal_server_error(e):
    """500 hata sayfası"""
    logger.error(f"500 hatası: {str(e)}", exc_info=True)
    return render_template('errors/500.html'), 500 