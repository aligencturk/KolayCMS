from flask import render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app.modules.page_builder.views import page_builder_bp
from app.models import PageTemplate, PageElement, Corporate, PageStyle, Component, ComponentCategory
from app.decorators import admin_required, editor_required
from app import db
from app.utils.firestore_manager import FirestoreManager
import uuid
from datetime import datetime
import json
import asyncio

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

@page_builder_bp.route('/live-editor/<page_id>')
@login_required
@editor_required
def live_editor(page_id):
    """Canlı sayfa düzenleyici"""
    # Sayfa bilgilerini getir
    page_ref = db.collection('corporate').document(page_id).get()
    if not page_ref.exists:
        flash('Sayfa bulunamadı', 'error')
        return redirect(url_for('page_builder.index'))
    
    page = Corporate(**page_ref.to_dict(), id=page_ref.id)
    
    # Komponent kategorilerini getir
    categories_ref = db.collection('component_categories').stream()
    categories = [ComponentCategory(**doc.to_dict(), id=doc.id) for doc in categories_ref]
    
    # Komponentleri getir
    components_ref = db.collection('components').stream()
    components = [Component(**doc.to_dict(), id=doc.id) for doc in components_ref]
    
    return render_template(
        'page_builder/live-editor.html', 
        page=page,
        categories=categories,
        components=components
    )

@page_builder_bp.route('/preview_page/<int:page_id>')
@login_required
@editor_required
def preview_page(page_id):
    """
    Sayfa veya şablon önizleme - iframe içinde gösterilecek
    Bu route hem sayfalar hem de şablonlar için ortak önizleme sağlar
    page_id=0 olduğunda ve template_id query parametresi verildiğinde
    şablon önizlemesi yapar
    """
    content_html = ""
    page_styles = {}
    
    # Şablon önizlemesi mi yoksa sayfa önizlemesi mi?
    template_id = request.args.get('template_id')
    if page_id == 0 and template_id:
        # Şablon önizlemesi
        template_ref = db.collection('page_templates').document(template_id).get()
        if not template_ref.exists:
            return "Şablon bulunamadı", 404
        
        template_data = template_ref.to_dict()
        template = PageTemplate(**template_data, id=template_ref.id)
        
        # Şablon içeriğini kullan
        content_html = template.content_html or """
        <div class="container mx-auto p-4">
            <h1 class="text-3xl font-bold mb-4">Şablon Önizlemesi</h1>
            <div class="bg-white p-6 rounded shadow">
                <p>Bu, şablon düzenleyici önizlemesidir.</p>
            </div>
            <div class="container mt-4" data-drop-zone="true">
                <!-- Buraya komponentler eklenebilir -->
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i> Komponentleri sürükleyip buraya bırakabilirsiniz.
                </div>
            </div>
        </div>
        """
        
        # Sayfa nesnesini oluştur
        page = Corporate(
            id=f"template_{template_id}",
            title=template.name,
            template_id=template_id,
            content_html=content_html
        )
        
        # Şablon stillerini al
        fs_manager = FirestoreManager()
        try:
            # Şablon ile ilişkili stil bilgilerini al
            template_styles = asyncio.run(fs_manager.get_template_styles(template_id))
            if template_styles:
                page_styles = template_styles
        except Exception as e:
            current_app.logger.error(f"Şablon stilleri alınırken hata: {str(e)}")
    else:
        # Normal sayfa önizlemesi
        page_ref = db.collection('corporate').document(str(page_id)).get()
        if not page_ref.exists:
            return "Sayfa bulunamadı", 404
        
        page_data = page_ref.to_dict()
        page = Corporate(**page_data, id=page_ref.id)
        
        # Sayfanın kendi içeriğini yükle
        if page.content_html:
            content_html = page.content_html
        else:
            # Eğer sayfa içeriği yoksa, basit bir içerik oluştur
            content_html = f"""
            <div class="container mx-auto p-4">
                <h1 class="text-3xl font-bold mb-4">{page.title}</h1>
                <div class="bg-white p-6 rounded shadow">
                    <p>Bu sayfa henüz içerik eklenmemiş bir sayfa düzenleyici önizlemesidir.</p>
                </div>
                <div class="container mt-4" data-drop-zone="true">
                    <!-- Buraya komponentler eklenebilir -->
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle"></i> Komponentleri sürükleyip buraya bırakabilirsiniz.
                    </div>
                </div>
            </div>
            """
        
        # Stil bilgilerini getir
        fs_manager = FirestoreManager()
        # Asenkron metodu çağırmak için asyncio.run kullan
        try:
            page_styles = asyncio.run(fs_manager.get_page_styles(str(page_id)))
        except Exception as e:
            current_app.logger.error(f"Sayfa stilleri alınırken hata: {str(e)}")
    
    # Önizleme şablonuna gönder
    return render_template('page_builder/preview.html', 
                          page=page, 
                          content_html=content_html,
                          page_styles=page_styles)

@page_builder_bp.route('/api/save-styles', methods=['POST'])
@login_required
@editor_required
def save_styles():
    """Sayfa stillerini kaydet"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'JSON veri gönderilmedi'}), 400
    
    # Gerekli alanları kontrol et
    required_fields = ['page_id', 'element_styles']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} alanı zorunludur'}), 400
    
    page_id = data['page_id']
    element_styles = data['element_styles']
    is_published = data.get('is_published', False)
    
    # Sayfa var mı kontrol et
    page_ref = db.collection('corporate').document(page_id)
    page_doc = page_ref.get()
    
    if not page_doc.exists:
        return jsonify({'error': 'Sayfa bulunamadı'}), 404
    
    try:
        # FirestoreManager ile stilleri kaydet
        fs_manager = FirestoreManager()
        
        # Asenkron metodu çağırmak için asyncio.run kullan
        success = asyncio.run(fs_manager.save_page_styles(
            page_id=page_id,
            styles_data={
                'element_styles': element_styles,
                'global_styles': data.get('global_styles', {})
            },
            is_published=is_published
        ))
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Sayfa stilleri başarıyla kaydedildi'
            })
        else:
            return jsonify({'error': 'Stiller kaydedilirken bir hata oluştu'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Hata: {str(e)}'}), 500

@page_builder_bp.route('/db-admin')
def db_admin():
    """Veritabanı yönetim sayfası"""
    try:
        # Günlükleme ekle
        print("db_admin fonksiyonu çağrıldı")
        
        # Debug için globals() içindeki db değişkenini kontrol et
        import sys
        print(f"sys.modules anahtarları: {list(sys.modules.keys())[:20]}...")
        print(f"globals anahtarları: {list(globals().keys())}")
        
        from app import db as app_db
        
        # Firebase bağlantısını kontrol et
        if not db:
            print("Firestore veritabanı bağlantısı yok!")
            # Alternatif db bağlantısını dene
            try:
                from firebase_admin import firestore
                alt_db = firestore.client()
                print(f"Alternatif firestore bağlantısı oluşturuldu: {alt_db}")
                
                # Tüm kullanıcıları getir
                users_ref = alt_db.collection('users').stream()
                users = []
                
                for doc in users_ref:
                    user_data = doc.to_dict()
                    user_data['id'] = doc.id
                    users.append(user_data)
                    print(f"Kullanıcı bulundu: {user_data.get('email')}")
                
                print(f"Toplam {len(users)} kullanıcı bulundu.")
                return render_template('page_builder/db_admin.html', users=users)
            except Exception as alt_e:
                print(f"Alternatif bağlantı hatası: {str(alt_e)}")
                flash('Veritabanı bağlantısı kurulamadı.', 'error')
                return render_template('page_builder/db_admin.html', users=[])
        
        print("Firestore bağlantısı mevcut, kullanıcıları getirmeye çalışıyorum...")
        
        # Tüm kullanıcıları getir
        users_ref = db.collection('users').stream()
        users = []
        
        for doc in users_ref:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            users.append(user_data)
            print(f"Kullanıcı bulundu: {user_data.get('email')}")
        
        print(f"Toplam {len(users)} kullanıcı bulundu.")
        return render_template('page_builder/db_admin.html', users=users)
    except Exception as e:
        # Detaylı hata bilgisi
        import traceback
        error_details = traceback.format_exc()
        print(f"DB_ADMIN HATA: {str(e)}")
        print(f"HATA DETAYLARI: {error_details}")
        
        # Hata oluştuğunda dahi şablonu boş kullanıcı listesiyle render etmeyi dene
        try:
            return render_template('page_builder/db_admin.html', users=[])
        except Exception as render_e:
            print(f"Render hatası: {str(render_e)}")
            flash(f'Kullanıcıları getirirken hata oluştu: {str(e)}', 'error')
            return redirect(url_for('main.dashboard'))

@page_builder_bp.route('/delete-user/<user_id>', methods=['GET'])
def delete_user(user_id):
    """Kullanıcıyı sil"""
    try:
        # Kullanıcıyı sil
        db.collection('users').document(user_id).delete()
        
        flash('Kullanıcı başarıyla silindi.', 'success')
        return redirect(url_for('page_builder.db_admin'))
    except Exception as e:
        flash(f'Kullanıcı silinirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('page_builder.db_admin'))

@page_builder_bp.route('/create-admin', methods=['GET', 'POST'])
def create_admin():
    """Yeni admin oluştur"""
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not email or not username or not password:
            flash('Tüm alanları doldurunuz.', 'error')
            return render_template('page_builder/create_admin.html')
        
        try:
            from firebase_admin import auth
            
            # Kullanıcıyı Firebase Authentication'da oluştur
            user_record = auth.create_user(
                email=email,
                password=password,
                display_name=username
            )
            
            # Firestore'a kullanıcı bilgilerini kaydet
            db.collection('users').document(user_record.uid).set({
                'email': email,
                'username': username,
                'role': 'admin',
                'is_active': True,
                'created_at': datetime.now(),
                'updated_at': datetime.now()
            })
            
            flash('Admin kullanıcı başarıyla oluşturuldu.', 'success')
            return redirect(url_for('page_builder.db_admin'))
        except Exception as e:
            flash(f'Admin oluşturulurken hata oluştu: {str(e)}', 'error')
            return render_template('page_builder/create_admin.html')
    
    return render_template('page_builder/create_admin.html')

@page_builder_bp.route('/set-default-admin')
def set_default_admin():
    """Varsayılan admin hesabını (admin@kolaycms.com) admin rolüne yükselt"""
    try:
        from firebase_admin import auth
        
        DEFAULT_ADMIN_EMAIL = "admin@kolaycms.com"
        DEFAULT_ADMIN_PASSWORD = "admin123"  # Bu varsayılan şifre olarak kullanılacak
        
        # admin@kolaycms.com e-posta adresine sahip kullanıcıyı bul
        try:
            users = auth.get_users_by_email(DEFAULT_ADMIN_EMAIL)
            
            if not users or not users.users:
                # Kullanıcı yoksa oluştur
                try:
                    user_record = auth.create_user(
                        email=DEFAULT_ADMIN_EMAIL,
                        password=DEFAULT_ADMIN_PASSWORD,
                        display_name="Admin Kullanıcı"
                    )
                    user_id = user_record.uid
                    
                    # Yeni kullanıcı olarak oluştur
                    db.collection('users').document(user_id).set({
                        'email': DEFAULT_ADMIN_EMAIL,
                        'username': "Admin Kullanıcı",
                        'role': 'admin',
                        'is_active': True,
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
                    
                    flash(f'Varsayılan admin hesabı ({DEFAULT_ADMIN_EMAIL}) oluşturuldu ve admin rolüne atandı.', 'success')
                except Exception as create_error:
                    flash(f'Varsayılan admin oluşturulurken hata: {str(create_error)}', 'error')
                    return redirect(url_for('page_builder.db_admin'))
            else:
                # Kullanıcı varsa rolünü güncelle
                user_record = users.users[0]
                user_id = user_record.uid
                
                # Kullanıcı veritabanında var mı kontrol et
                user_db_ref = db.collection('users').document(user_id).get()
                
                if user_db_ref.exists:
                    # Kullanıcının rolünü admin olarak güncelle
                    db.collection('users').document(user_id).update({
                        'role': 'admin',
                        'is_active': True,
                        'updated_at': datetime.now()
                    })
                    flash(f'Varsayılan admin hesabı ({DEFAULT_ADMIN_EMAIL}) başarıyla admin rolüne yükseltildi.', 'success')
                else:
                    # Kullanıcı Authentication'da var ama veritabanında yoksa ekle
                    db.collection('users').document(user_id).set({
                        'email': DEFAULT_ADMIN_EMAIL,
                        'username': user_record.display_name or "Admin Kullanıcı",
                        'role': 'admin',
                        'is_active': True,
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    })
                    flash(f'Varsayılan admin hesabı ({DEFAULT_ADMIN_EMAIL}) veritabanına eklendi ve admin rolüne atandı.', 'success')
                
        except Exception as user_error:
            flash(f'Kullanıcı bilgileri alınırken hata: {str(user_error)}', 'error')
            return redirect(url_for('page_builder.db_admin'))
                
        return redirect(url_for('page_builder.db_admin'))
    except Exception as e:
        flash(f'Admin rolü güncellenirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('page_builder.db_admin'))

@page_builder_bp.route('/api/components', methods=['GET'])
@login_required
@editor_required
def get_components():
    """Komponentleri getir"""
    # Filtre parametrelerini al
    category_id = request.args.get('category_id')
    
    # Sorgu oluştur
    query = db.collection('components')
    
    # Kategori filtresi varsa ekle
    if category_id:
        query = query.where('category_id', '==', category_id)
    
    # Sorguyu çalıştır
    components_ref = query.stream()
    components = [{"id": doc.id, **doc.to_dict()} for doc in components_ref]
    
    return jsonify(components)

@page_builder_bp.route('/api/components', methods=['POST'])
@login_required
@admin_required
def create_component():
    """Yeni bir komponent oluştur"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'JSON veri gönderilmedi'}), 400
    
    # Gerekli alanları kontrol et
    required_fields = ['name', 'html_template', 'icon', 'category_id']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} alanı zorunludur'}), 400
    
    # Yeni komponent oluştur
    component_id = str(uuid.uuid4())
    component_data = {
        'name': data['name'],
        'html_template': data['html_template'],
        'icon': data['icon'],
        'category_id': data['category_id'],
        'description': data.get('description', ''),
        'default_props': data.get('default_props', {}),
        'created_at': datetime.now(),
        'created_by': current_user.id
    }
    
    # Komponenti veritabanına ekle
    db.collection('components').document(component_id).set(component_data)
    
    return jsonify({
        'success': True,
        'message': 'Komponent başarıyla oluşturuldu',
        'component_id': component_id
    })

@page_builder_bp.route('/api/components/<component_id>', methods=['PUT'])
@login_required
@admin_required
def update_component(component_id):
    """Komponenti güncelle"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'JSON veri gönderilmedi'}), 400
    
    # Komponentin var olduğunu kontrol et
    component_ref = db.collection('components').document(component_id)
    component_doc = component_ref.get()
    
    if not component_doc.exists:
        return jsonify({'error': 'Komponent bulunamadı'}), 404
    
    # Güncellenecek alanları belirle
    update_data = {}
    updatable_fields = ['name', 'html_template', 'icon', 'category_id', 'description', 'default_props']
    
    for field in updatable_fields:
        if field in data:
            update_data[field] = data[field]
    
    # Son güncelleme bilgilerini ekle
    update_data['updated_at'] = datetime.now()
    update_data['updated_by'] = current_user.id
    
    # Komponenti güncelle
    component_ref.update(update_data)
    
    return jsonify({
        'success': True,
        'message': 'Komponent başarıyla güncellendi'
    })

@page_builder_bp.route('/api/components/<component_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_component(component_id):
    """Komponenti sil"""
    # Komponentin var olduğunu kontrol et
    component_ref = db.collection('components').document(component_id)
    component_doc = component_ref.get()
    
    if not component_doc.exists:
        return jsonify({'error': 'Komponent bulunamadı'}), 404
    
    # Komponenti sil
    component_ref.delete()
    
    return jsonify({
        'success': True,
        'message': 'Komponent başarıyla silindi'
    })

@page_builder_bp.route('/api/component-categories', methods=['GET'])
@login_required
@editor_required
def get_component_categories():
    """Komponent kategorilerini getir"""
    categories_ref = db.collection('component_categories').stream()
    categories = [{"id": doc.id, **doc.to_dict()} for doc in categories_ref]
    
    return jsonify(categories)

@page_builder_bp.route('/api/component-categories', methods=['POST'])
@login_required
@admin_required
def create_component_category():
    """Yeni bir komponent kategorisi oluştur"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'JSON veri gönderilmedi'}), 400
    
    # Gerekli alanları kontrol et
    if 'name' not in data:
        return jsonify({'error': 'name alanı zorunludur'}), 400
    
    # Yeni kategori oluştur
    category_id = str(uuid.uuid4())
    category_data = {
        'name': data['name'],
        'description': data.get('description', ''),
        'icon': data.get('icon', 'fa-folder'),
        'created_at': datetime.now(),
        'created_by': current_user.id
    }
    
    # Kategoriyi veritabanına ekle
    db.collection('component_categories').document(category_id).set(category_data)
    
    return jsonify({
        'success': True,
        'message': 'Kategori başarıyla oluşturuldu',
        'category_id': category_id
    })

@page_builder_bp.route('/api/save-page-content', methods=['POST'])
@login_required
@editor_required
def save_page_content():
    """Sayfa içeriğini HTML olarak kaydet"""
    data = request.json
    
    if not data:
        return jsonify({'error': 'JSON veri gönderilmedi'}), 400
    
    # Gerekli alanları kontrol et
    required_fields = ['page_id', 'content_html']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'{field} alanı zorunludur'}), 400
    
    page_id = data['page_id']
    content_html = data['content_html']
    is_published = data.get('is_published', False)
    
    # Sayfa var mı kontrol et
    page_ref = db.collection('corporate').document(page_id)
    page_doc = page_ref.get()
    
    if not page_doc.exists:
        return jsonify({'error': 'Sayfa bulunamadı'}), 404
    
    # Sayfayı güncelle
    update_data = {
        'content_html': content_html,
        'updated_at': datetime.now(),
        'updated_by': current_user.id
    }
    
    # Eğer yayınlanacaksa
    if is_published:
        update_data['published_content_html'] = content_html
        update_data['published_at'] = datetime.now()
        update_data['is_published'] = True
    
    # Sayfayı güncelle
    page_ref.update(update_data)
    
    return jsonify({
        'success': True,
        'message': 'Sayfa içeriği başarıyla kaydedildi'
    }) 