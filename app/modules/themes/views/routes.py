import json
import os
import uuid
import re
import zipfile
import tempfile
import shutil
import tarfile
import datetime
from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, session, flash, current_app, jsonify, g, abort, Response, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, logger, storage
from . import themes_bp
from app.services.theme_service import ThemeService
from app.modules.themes.models import Theme
from app.decorators import admin_required
# Firebase Firestore için import
from google.cloud import firestore
import traceback
import jinja2
import re  # Regex işlemleri için eklendi

# ThemeTemplate sınıfı tanımı
class ThemeTemplate:
    def __init__(self, id=None, theme_id=None, name=None, description=None, content=None, created_at=None, updated_at=None):
        self.id = id
        self.theme_id = theme_id
        self.name = name
        self.description = description
        self.content = content
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    @staticmethod
    def from_dict(data, id=None):
        template = ThemeTemplate(
            id=id,
            theme_id=data.get('theme_id'),
            name=data.get('name'),
            description=data.get('description'),
            content=data.get('content'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
        return template

# Diğer gerekli sınıf tanımlamaları
class ThemeComponent:
    def __init__(self, id=None, theme_id=None, name=None, description=None, html=None, css=None, js=None, is_global=False, **kwargs):
        self.id = id
        self.theme_id = theme_id
        self.name = name
        self.description = description
        self.html = html
        self.css = css
        self.js = js
        self.is_global = is_global
        for key, value in kwargs.items():
            setattr(self, key, value)

class PageTemplate:
    def __init__(self, id=None, name=None, description=None, template_type=None, html_content=None, is_active=True, created_at=None, updated_at=None, created_by=None, updated_by=None, **kwargs):
        self.id = id
        self.name = name
        self.description = description
        self.template_type = template_type
        self.html_content = html_content
        self.is_active = is_active
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.created_by = created_by
        self.updated_by = updated_by
        self.html_structure = html_content
        self.content = kwargs.get('content', {})
        for key, value in kwargs.items():
            if not hasattr(self, key):
                setattr(self, key, value)
    
    @staticmethod
    def from_dict(data, id=None):
        return PageTemplate(id=id, **data)

class Corporate:
    def __init__(self, id=None, title=None, content=None, page_type=None, meta_description=None, template_id=None, created_at=None, updated_at=None, created_by=None, updated_by=None, **kwargs):
        self.id = id
        self.title = title
        self.content = content
        self.page_type = page_type
        self.meta_description = meta_description
        self.template_id = template_id
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        self.created_by = created_by
        self.updated_by = updated_by
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

class PageElement:
    def __init__(self, id=None, page_id=None, element_type=None, content=None, position=None, created_at=None, updated_at=None, **kwargs):
        self.id = id
        self.page_id = page_id
        self.element_type = element_type
        self.content = content
        self.position = position
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_')}

class Component:
    def __init__(self, id=None, name=None, description=None, component_type=None, html=None, css=None, js=None, is_active=True, **kwargs):
        self.id = id
        self.name = name
        self.description = description
        self.component_type = component_type
        self.html = html
        self.css = css
        self.js = js
        self.is_active = is_active
        for key, value in kwargs.items():
            setattr(self, key, value)

# patoolib importu (dosya sıkıştırma işlemleri için)
try:
    import patoolib
except ImportError:
    # patoolib yüklü değilse, sahte bir fonksiyon tanımlayalım
    def patoolib_extract_archive_fallback(*args, **kwargs):
        logger.error("patoolib kütüphanesi yüklü değil. RAR dosyaları açılamayacak.")
        raise ImportError("patoolib kütüphanesi yüklü değil")
    
    # patoolib modülüne sahte fonksiyon ekleyerek tanımlıyoruz
    class PatoolibMock:
        @staticmethod
        def extract_archive(*args, **kwargs):
            return patoolib_extract_archive_fallback(*args, **kwargs)
    
    patoolib = PatoolibMock()

@themes_bp.route('/')
@login_required
@admin_required
def index():
    """Tema yönetimi ana sayfası"""
    try:
        current_app.logger.debug("Temalar getiriliyor...")
        themes_ref = db.collection('themes').stream()
        themes = []

        # Tema referanslarını say
        theme_count = 0
        for _ in db.collection('themes').stream():
            theme_count += 1
        
        current_app.logger.debug(f"Veritabanında {theme_count} tema bulundu")

        # Tema verilerini al
        for doc in themes_ref:
            theme_data = doc.to_dict()
            theme_data['id'] = doc.id
            current_app.logger.debug(f"Firestore tema verisi: {theme_data}")

            theme = Theme.from_dict(theme_data, doc.id)
            if theme:
                themes.append(theme)
                current_app.logger.debug(f"Tema nesnesi oluşturuldu: {theme.name}")
            else:
                current_app.logger.error(f"Tema oluşturulamadı: {doc.id}")

        theme_list = [theme.to_dict() for theme in themes]
        current_app.logger.debug(f"Şablona gönderilen tema listesi: {theme_list}")
        
        # Debug modunda flask.g ile tema listesini paylaş
        if current_app.config.get('DEBUG'):
            g.theme_list = theme_list

        return render_template('themes/index.html', themes=theme_list)
    except Exception as e:
        current_app.logger.error(f"Tema listesi alınırken hata oluştu: {str(e)}", exc_info=True)
        flash('Temalar yüklenirken bir hata oluştu.', 'error')
        return render_template('themes/index.html', themes=[])

@themes_bp.route('/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_theme():
    """Yeni tema oluşturma"""
    if request.method == 'POST':
        try:
            # Form verilerini al
            name = request.form.get('name')
            description = request.form.get('description')
            author = request.form.get('author', current_user.username)  # Varsayılan olarak mevcut kullanıcı
            version = request.form.get('version', '1.0.0')
            primary_color = request.form.get('primary_color', '#00BCD4')
            secondary_color = request.form.get('secondary_color', '#f44336')
            font_family = request.form.get('font_family', '')
            css_variables = request.form.get('css_variables', '')
            is_active = True if request.form.get('is_active') else False
            
            # Yeni tema oluştur
            theme_id = str(uuid.uuid4())
            theme = Theme(
                id=theme_id,
                name=name,
                description=description,
                author=author,
                version=version,
                is_active=is_active,
                thumbnail_url=request.form.get('thumbnail_url', ''),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                created_by=current_user.uid
            )
            
            # Eğer bu tema aktif olarak işaretlendiyse, diğer temaları deaktif yap
            if is_active:
                themes_ref = db.collection('themes').where('is_active', '==', True).stream()
                for doc in themes_ref:
                    db.collection('themes').document(doc.id).update({'is_active': False})
            
            # Firestore'a kaydet
            db.collection('themes').document(theme_id).set(theme.to_dict())
            
            # Tema için CSS dosyası oluştur
            css_content = f"""
:root {{
    --primary-color: {primary_color};
    --secondary-color: {secondary_color};
    {css_variables}
}}

body {{
    font-family: {font_family if font_family else 'inherit'};
}}
"""
            
            # Tema dizinlerini oluştur
            theme_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'themes', theme_id)
            css_dir = os.path.join(theme_dir, 'css')
            js_dir = os.path.join(theme_dir, 'js')
            templates_dir = os.path.join(theme_dir, 'templates')
            
            os.makedirs(css_dir, exist_ok=True)
            os.makedirs(js_dir, exist_ok=True)
            os.makedirs(templates_dir, exist_ok=True)
            
            # CSS dosyasını kaydet
            with open(os.path.join(css_dir, 'theme.css'), 'w', encoding='utf-8') as f:
                f.write(css_content)
            
            # Tema dizinlerini güncelle
            db.collection('themes').document(theme_id).update({
                'template_dir': f'themes/{theme_id}/templates',
                'css_dir': f'themes/{theme_id}/css',
                'js_dir': f'themes/{theme_id}/js'
            })
            
            flash(f'Tema "{name}" başarıyla oluşturuldu.', 'success')
            return redirect(url_for('themes.index'))
        except Exception as e:
            current_app.logger.error(f"Tema oluşturma hatası: {str(e)}")
            flash(f'Tema oluşturulurken bir hata oluştu: {str(e)}', 'error')
            return render_template('themes/create.html', form=request.form)
        
    return render_template('themes/create.html')

@themes_bp.route('/edit/<theme_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_theme(theme_id):
    """Tema düzenleme"""
    theme_ref = db.collection('themes').document(theme_id).get()
    if not theme_ref.exists:
        flash('Tema bulunamadı', 'error')
        return redirect(url_for('themes.index'))
        
    theme = Theme.from_dict(theme_ref.to_dict(), theme_ref.id)
    
    if request.method == 'POST':
        # Form verilerini al ve temayı güncelle
        theme.name = request.form.get('name')
        theme.description = request.form.get('description')
        theme.author = request.form.get('author')
        theme.version = request.form.get('version', '1.0.0')
        theme.thumbnail_url = request.form.get('thumbnail_url', theme.thumbnail_url)
        theme.updated_at = datetime.now()
        
        # Firestore'a kaydet
        db.collection('themes').document(theme_id).update(theme.to_dict())
        
        flash(f'Tema "{theme.name}" başarıyla güncellendi.', 'success')
        return redirect(url_for('themes.index'))
    
    return render_template('themes/edit.html', theme=theme)

@themes_bp.route('/toggle-active/<theme_id>', methods=['POST'])
@login_required
@admin_required
def toggle_active(theme_id):
    """Tema aktifleştirme/deaktifleştirme"""
    try:
        # Temayı getir
        theme_ref = db.collection('themes').document(theme_id)
        theme_doc = theme_ref.get()
        
        if not theme_doc.exists:
            flash('Tema bulunamadı.', 'error')
            return redirect(url_for('themes.index'))
        
        # Diğer tüm temaları deaktif yap
        themes_ref = db.collection('themes').where('is_active', '==', True).stream()
        for doc in themes_ref:
            db.collection('themes').document(doc.id).update({'is_active': False})
        
        # Bu temayı aktif yap
        theme_ref.update({'is_active': True})
        
        # Success mesajı
        flash('Tema başarıyla aktifleştirildi.', 'success')
        
        # İstek AJAX ise JSON yanıt döndür, değilse yönlendir
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'message': 'Tema başarıyla aktifleştirildi.'})
            
        # Doğrudan tema sayfasına yönlendir
        return redirect(url_for('themes.index'))
    except Exception as e:
        current_app.logger.error(f"Tema aktifleştirme hatası: {str(e)}")
        flash('Tema aktifleştirilirken bir hata oluştu.', 'error')
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'error': 'Tema aktifleştirilirken bir hata oluştu.'}), 500
        return redirect(url_for('themes.index'))

@themes_bp.route('/delete/<theme_id>', methods=['POST'])
@login_required
@admin_required
def delete_theme(theme_id):
    """Tema silme işlemi"""
    try:
        # Temayı veritabanından sorgula
        theme_doc = db.collection('themes').document(theme_id).get()
        
        if not theme_doc.exists:
            flash('Tema bulunamadı.', 'error')
            return redirect(url_for('themes.index'))
        
        theme_data = theme_doc.to_dict()
        theme_name = theme_data.get('name', 'Bilinmeyen Tema')
        
        # Tema aktif mi kontrol et
        if theme_data.get('is_active', False):
            flash('Aktif bir temayı silemezsiniz. Önce başka bir temayı aktif yapın.', 'error')
            return redirect(url_for('themes.index'))
        
        # Tema ile ilişkili kaynakları temizle
        # 1. Tema şablonlarını sil
        templates_ref = db.collection('theme_templates').where('theme_id', '==', theme_id).stream()
        for template in templates_ref:
            db.collection('theme_templates').document(template.id).delete()
        
        # 2. Tema bileşenlerini sil
        components_ref = db.collection('theme_components').where('theme_id', '==', theme_id).stream()
        for component in components_ref:
            db.collection('theme_components').document(component.id).delete()
        
        # 3. Temayı veritabanından sil
        db.collection('themes').document(theme_id).delete()
        
        # 4. Tema dosyalarını disk üzerinden sil
        theme_dir = os.path.join(current_app.root_path, '..', 'themes', theme_id)
        if os.path.exists(theme_dir):
            try:
                import shutil
                shutil.rmtree(theme_dir)
                current_app.logger.info(f"Tema dosyaları silindi: {theme_dir}")
            except Exception as e:
                current_app.logger.error(f"Tema dosyaları silinirken hata oluştu: {str(e)}", exc_info=True)
                # Veritabanı işlemi zaten tamamlandığı için sadece uyarı ver
                flash(f"Tema veritabanından silindi, ancak dosyaları silinirken hata oluştu: {str(e)}", 'warning')
                return redirect(url_for('themes.index'))
        
        flash(f'"{theme_name}" teması başarıyla silindi.', 'success')
        return redirect(url_for('themes.index'))
    
    except Exception as e:
        flash(f'Tema silinirken bir hata oluştu: {str(e)}', 'error')
        current_app.logger.error(f"Tema silme hatası: {str(e)}", exc_info=True)
        return redirect(url_for('themes.index'))

@themes_bp.route('/upload', methods=['GET', 'POST'])
@login_required
@admin_required
def upload_theme():
    if request.method == 'POST':
        # ZIP veya RAR dosyası olup olmadığını kontrol et
        if 'theme_file' not in request.files:
            current_app.logger.error("Tema dosyası yüklenemedi: Dosya yok")
            flash('Tema dosyası seçilmedi.', 'error')
            return redirect(url_for('themes.index'))
        
        theme_file = request.files['theme_file']
        
        if theme_file.filename == '':
            current_app.logger.error("Tema dosyası yüklenemedi: Dosya adı boş")
            flash('Dosya seçilmedi.', 'error')
            return redirect(url_for('themes.index'))
        
        if not (theme_file.filename.endswith('.zip') or theme_file.filename.endswith('.rar')):
            current_app.logger.error(f"Tema dosyası yüklenemedi: Desteklenmeyen format: {theme_file.filename}")
            flash('Sadece ZIP veya RAR formatında dosya yükleyebilirsiniz.', 'error')
            return redirect(url_for('themes.index'))
        
        # Tema adını al
        theme_name = request.form.get('theme_name', '')
        if not theme_name:
            # Dosya adından tema adı oluştur
            theme_name = os.path.splitext(theme_file.filename)[0]
        
        # Benzersiz tema ID'si oluştur
        theme_id = str(uuid.uuid4())
        
        # Tema yolları oluştur
        theme_dir = os.path.join(current_app.root_path, '..', 'themes', theme_id)
        template_dir = os.path.join(theme_dir, 'templates')
        static_dir = os.path.join(theme_dir, 'static')
        css_dir = os.path.join(static_dir, 'css')
        js_dir = os.path.join(static_dir, 'js')
        img_dir = os.path.join(static_dir, 'images')
        temp_dir = os.path.join(current_app.root_path, '..', 'temp', theme_id)
        
        # Tema yollarını ayrıntılı olarak logla
        current_app.logger.info(f"Tema dizini oluşturuluyor: {os.path.abspath(theme_dir)}")
        current_app.logger.info(f"Ana uygulama dizini: {os.path.abspath(current_app.root_path)}")
        
        try:
            # Geçici dizin ve tema dizinlerini oluştur
            os.makedirs(temp_dir, exist_ok=True)
            os.makedirs(template_dir, exist_ok=True)
            os.makedirs(static_dir, exist_ok=True)
            os.makedirs(css_dir, exist_ok=True)
            os.makedirs(js_dir, exist_ok=True)
            os.makedirs(img_dir, exist_ok=True)
            
            # Dosyayı geçici dizine kaydet
            temp_file_path = os.path.join(temp_dir, theme_file.filename)
            theme_file.save(temp_file_path)
            current_app.logger.debug(f"Tema dosyası geçici dizine kaydedildi: {temp_file_path}")
            
            # ZIP veya RAR dosyasını çıkart
            try:
                current_app.logger.debug(f"Tema arşivi çıkartılıyor: {temp_file_path}")
                patoolib.extract_archive(temp_file_path, outdir=temp_dir)
                os.remove(temp_file_path)  # Arşiv dosyasını sil
                current_app.logger.debug("Tema arşivi çıkartıldı ve geçici dosya silindi")
            except Exception as extract_error:
                current_app.logger.error(f"Arşiv çıkartılamadı: {str(extract_error)}", exc_info=True)
                try:
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    current_app.logger.debug(f"Geçici dizin temizlendi: {temp_dir}")
                except Exception as cleanup_error:
                    current_app.logger.error(f"Geçici dizin temizleme hatası: {str(cleanup_error)}")
                
                flash(f'Tema arşivi çıkartılamadı: {str(extract_error)}', 'error')
                return redirect(url_for('themes.index'))
            
            # Çıkartılan dosyaları analiz et ve doğru klasörlere taşı
            html_files = []
            css_files = []
            js_files = []
            img_files = []
            
            # Geçici dizindeki tüm dosyaları tara
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # HTML dosyalarını templates dizinine taşı
                    if file.endswith('.html'):
                        dest_path = os.path.join(template_dir, file)
                        shutil.copy2(file_path, dest_path)
                        html_files.append(file)
                        
                    # CSS dosyalarını css dizinine taşı
                    elif file.endswith('.css'):
                        dest_path = os.path.join(css_dir, file)
                        shutil.copy2(file_path, dest_path)
                        css_files.append(file)
                        
                    # JS dosyalarını js dizinine taşı
                    elif file.endswith('.js'):
                        dest_path = os.path.join(js_dir, file)
                        shutil.copy2(file_path, dest_path)
                        js_files.append(file)
                        
                    # Resim dosyalarını images dizinine taşı
                    elif file.endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg')):
                        dest_path = os.path.join(img_dir, file)
                        shutil.copy2(file_path, dest_path)
                        img_files.append(file)
            
            current_app.logger.debug(f"HTML: {html_files}, CSS: {css_files}, JS: {js_files}, IMG: {img_files}")
            
            # HTML şablonu yoksa oluştur
            if not html_files:
                current_app.logger.warning("HTML şablonu bulunamadı, varsayılan oluşturuluyor")
                # Varsayılan index.html oluştur
                index_html_path = os.path.join(template_dir, 'index.html')
                with open(index_html_path, 'w', encoding='utf-8') as f:
                    f.write("""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ site_title }}</title>
    <link rel="stylesheet" href="/themes/{{ theme_id }}/static/css/style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>{{ site_name }}</h1>
            <nav>
                <ul>
                    <li><a href="/">Ana Sayfa</a></li>
                    <li><a href="/hakkimizda">Hakkımızda</a></li>
                    <li><a href="/hizmetlerimiz">Hizmetlerimiz</a></li>
                    <li><a href="/iletisim">İletişim</a></li>
                </ul>
            </nav>
        </div>
    </header>

    <main>
        <div class="container">
            <h2>{{ page_title }}</h2>
            <div class="content">
                {{ page_content|safe }}
            </div>
        </div>
    </main>

    <footer>
        <div class="container">
            <p>&copy; {{ site_name }} - {{ current_year }}</p>
        </div>
    </footer>
</body>
</html>""")
                html_files.append('index.html')
                current_app.logger.debug("Varsayılan index.html oluşturuldu")
            
            # CSS şablonu yoksa oluştur
            if not css_files:
                current_app.logger.warning("CSS dosyası bulunamadı, varsayılan oluşturuluyor")
                # Varsayılan style.css oluştur
                style_css_path = os.path.join(css_dir, 'style.css')
                with open(style_css_path, 'w', encoding='utf-8') as f:
                    f.write("""/* Temel CSS */
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.6;
    color: #333;
}

.container {
    width: 80%;
    margin: 0 auto;
    padding: 20px;
}

header {
    background-color: #333;
    color: white;
    padding: 1rem 0;
}

header h1 {
    color: white;
    margin-top: 0;
}
nav ul {
    list-style: none;
    padding: 0;
    display: flex;
    flex-wrap: wrap;
}
nav ul li {
    margin-right: 20px;
}
nav ul li a {
    color: white;
    text-decoration: none;
}
nav ul li a:hover {
    text-decoration: underline;
}
""")
                css_files.append('style.css')
                current_app.logger.debug("Varsayılan style.css oluşturuldu")
            
            # Tema bilgilerini veritabanına kaydet
            theme_data = {
                'id': theme_id,
                'name': theme_name,
                'description': request.form.get('theme_description', f'{theme_name} teması'),
                'version': request.form.get('theme_version', '1.0'),
                'author': request.form.get('theme_author', 'Admin'),
                'active': False,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'template_dir': os.path.join('themes', theme_id, 'templates'),
                'static_dir': os.path.join('themes', theme_id, 'static'),
                'thumbnail': '',
                'files': {
                    'html': html_files,
                    'css': css_files,
                    'js': js_files,
                    'images': img_files
                }
            }
            
            db.collection('themes').document(theme_id).set(theme_data)
            current_app.logger.info(f"Tema veritabanına kaydedildi: {theme_id} - {theme_name}")
            
            # Geçici dizini temizle
            shutil.rmtree(temp_dir, ignore_errors=True)
            current_app.logger.debug(f"Geçici dizin temizlendi: {temp_dir}")
            
            flash(f'"{theme_name}" teması başarıyla yüklendi.', 'success')
            return redirect(url_for('themes.index'))
            
        except Exception as e:
            current_app.logger.error(f"Tema yükleme hatası: {str(e)}", exc_info=True)
            # Hata durumunda dizinleri temizle
            try:
                shutil.rmtree(theme_dir, ignore_errors=True)
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception as cleanup_error:
                current_app.logger.error(f"Dizin temizleme hatası: {str(cleanup_error)}")
            
            flash(f'Tema yüklenirken hata oluştu: {str(e)}', 'error')
            return redirect(url_for('themes.index'))
    
    return render_template('themes/upload.html')

def process_theme_files(theme_dir, theme_name):
    """Tema dosyalarını uygun dizinlere yerleştir ve içeriği analiz et"""
    try:
        # HTML şablonlarını kopyala ve analiz et
        templates_dir = os.path.join(theme_dir, 'templates')
        if os.path.exists(templates_dir):
            dest_templates = os.path.join(current_app.root_path, 'templates', 'website', 'themes', theme_name)
            os.makedirs(dest_templates, exist_ok=True)
            
            # Şablonları analiz et ve veritabanına kaydet
            for root, dirs, files in os.walk(templates_dir):
                for file in files:
                    if file.endswith('.html'):
                        template_path = os.path.join(root, file)
                        relative_path = os.path.relpath(template_path, templates_dir)
                        dest_path = os.path.join(dest_templates, relative_path)
                        
                        # Şablon içeriğini oku
                        with open(template_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        # Şablon türünü belirle
                        template_type = 'page'  # Varsayılan olarak sayfa şablonu
                        if 'layout' in relative_path.lower():
                            template_type = 'layout'
                        elif 'component' in relative_path.lower():
                            template_type = 'component'
                        
                        # Şablon adını belirle
                        template_name = os.path.splitext(file)[0].replace('_', ' ').title()
                        
                        # Şablonu veritabanına kaydet
                        template_id = str(uuid.uuid4())
                        template = PageTemplate(
                            id=template_id,
                            name=template_name,
                            description=f"{template_name} şablonu",
                            template_type=template_type,
                            html_content=content,
                            is_active=True,
                            created_at=datetime.now(),
                            updated_at=datetime.now(),
                            created_by=current_user.uid if hasattr(current_user, 'uid') else None,
                            updated_by=current_user.uid if hasattr(current_user, 'uid') else None
                        )
                        
                        db.collection('page_templates').document(template_id).set(template.to_dict())
                        
                        # Dosyayı hedef konuma kopyala
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy2(template_path, dest_path)
        
        # CSS dosyalarını kopyala
        css_dir = os.path.join(theme_dir, 'css')
        if os.path.exists(css_dir):
            dest_css = os.path.join(current_app.root_path, 'static', 'css', 'themes', theme_name)
            os.makedirs(dest_css, exist_ok=True)
            copy_directory_contents(css_dir, dest_css)
        
        # JS dosyalarını kopyala
        js_dir = os.path.join(theme_dir, 'js')
        if os.path.exists(js_dir):
            dest_js = os.path.join(current_app.root_path, 'static', 'js', 'themes', theme_name)
            os.makedirs(dest_js, exist_ok=True)
            copy_directory_contents(js_dir, dest_js)
        
        # Resimleri kopyala
        img_dir = os.path.join(theme_dir, 'img')
        if os.path.exists(img_dir):
            dest_img = os.path.join(current_app.root_path, 'static', 'img', 'themes', theme_name)
            os.makedirs(dest_img, exist_ok=True)
            copy_directory_contents(img_dir, dest_img)
        
        # Tema konfigürasyonunu oku ve sayfaları oluştur
        theme_config_path = os.path.join(theme_dir, 'theme.json')
        if os.path.exists(theme_config_path):
            with open(theme_config_path, 'r', encoding='utf-8') as f:
                theme_config = json.load(f)
                
            # Sayfaları oluştur
            if 'pages' in theme_config:
                for page_data in theme_config['pages']:
                    page_id = str(uuid.uuid4())
                    page = Corporate(
                        id=page_id,
                        title=page_data.get('title', ''),
                        content=page_data.get('content', ''),
                        page_type=page_data.get('page_type', 'page'),
                        meta_description=page_data.get('meta_description', ''),
                        created_at=datetime.now(),
                        updated_at=datetime.now(),
                        created_by=current_user.uid if hasattr(current_user, 'uid') else None,
                        updated_by=current_user.uid if hasattr(current_user, 'uid') else None
                    )
                    
                    # Sayfa şablonunu belirle
                    if 'template' in page_data:
                        template_ref = db.collection('page_templates').where('name', '==', page_data['template']).limit(1).stream()
                        for doc in template_ref:
                            page.template_id = doc.id
                            break
                    
                    db.collection('corporate').document(page_id).set(page.to_dict())
                    
                    # Sayfa elementlerini oluştur
                    if 'elements' in page_data:
                        for element_data in page_data['elements']:
                            element_id = str(uuid.uuid4())
                            element = PageElement(
                                id=element_id,
                                page_id=page_id,
                                element_type=element_data.get('type', 'text'),
                                content=element_data.get('content', {}),
                                position=element_data.get('position', {'x': 0, 'y': 0, 'width': 12, 'height': 1}),
                                created_at=datetime.now(),
                                updated_at=datetime.now()
                            )
                            
                            db.collection('page_elements').document(element_id).set(element.to_dict())
    except Exception as e:
        current_app.logger.error(f"Tema dosyalarını işlerken hata: {str(e)}")
        raise

def copy_directory_contents(src, dest):
    """Bir dizinin içeriğini başka bir dizine kopyala"""
    for item in os.listdir(src):
        src_item = os.path.join(src, item)
        dest_item = os.path.join(dest, item)
        
        if os.path.isdir(src_item):
            os.makedirs(dest_item, exist_ok=True)
            copy_directory_contents(src_item, dest_item)
        else:
            shutil.copy2(src_item, dest_item)

@themes_bp.route('/editor/<theme_id>', methods=['GET'])
@login_required
@admin_required
def theme_editor(theme_id):
    """Tema düzenleyici sayfası"""
    theme_ref = db.collection('themes').document(theme_id).get()
    if not theme_ref.exists:
        flash('Tema bulunamadı', 'error')
        return redirect(url_for('themes.index'))
    
    theme = Theme.from_dict(theme_ref.to_dict(), theme_ref.id)
    
    # Tema şablonlarını getir
    templates_ref = db.collection('theme_templates').where('theme_id', '==', theme_id).stream()
    templates = [ThemeTemplate.from_dict(doc.to_dict(), doc.id) for doc in templates_ref]
    
    # Tema bileşenlerini getir
    components_ref = db.collection('theme_components').where('theme_id', '==', theme_id).stream()
    components = [ThemeComponent(**doc.to_dict(), id=doc.id) for doc in components_ref]
    
    return render_template(
        'themes/editor.html',
        theme=theme,
        templates=templates,
        components=components
    )

@themes_bp.route('/api/templates/<template_id>', methods=['GET'])
@login_required
@admin_required
def get_template(template_id):
    """Şablon içeriğini API ile getir"""
    template_ref = db.collection('theme_templates').document(template_id).get()
    if not template_ref.exists:
        return jsonify({'error': 'Şablon bulunamadı'}), 404
    
    template = ThemeTemplate.from_dict(template_ref.to_dict(), template_id)
    
    # Şablon içeriğini oku
    theme_ref = db.collection('themes').document(template.theme_id).get()
    theme = Theme.from_dict(theme_ref.to_dict(), theme_ref.id)
    
    template_path = os.path.join(current_app.root_path, 'templates', template.template_path)
    if not os.path.exists(template_path):
        return jsonify({'error': 'Şablon dosyası bulunamadı'}), 404
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    return jsonify({
        'id': template.id,
        'name': template.name,
        'description': template.description,
        'content': template_content,
        'theme_id': template.theme_id,
        'theme_name': theme.name
    })

@themes_bp.route('/api/templates/<template_id>', methods=['PUT'])
@login_required
@admin_required
def update_template(template_id):
    """Şablon içeriğini güncelle"""
    data = request.json
    if not data or 'content' not in data:
        return jsonify({'error': 'İçerik bulunamadı'}), 400
    
    template_ref = db.collection('theme_templates').document(template_id).get()
    if not template_ref.exists:
        return jsonify({'error': 'Şablon bulunamadı'}), 404
    
    template = ThemeTemplate.from_dict(template_ref.to_dict(), template_id)
    
    # Şablon dosyasını güncelle
    template_path = os.path.join(current_app.root_path, 'templates', template.template_path)
    try:
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(data['content'])
        
        # Veritabanındaki şablon bilgilerini güncelle
        if 'name' in data:
            template.name = data['name']
        if 'description' in data:
            template.description = data['description']
        
        template.updated_at = datetime.now()
        db.collection('theme_templates').document(template_id).update(template.to_dict())
        
        return jsonify({'message': 'Şablon başarıyla güncellendi'})
    except Exception as e:
        return jsonify({'error': f'Şablon güncellenirken hata oluştu: {str(e)}'}), 500

@themes_bp.route('/visual-editor/<template_id>', methods=['GET'])
@login_required
@admin_required
def visual_editor(template_id):
    """Görsel şablon düzenleyici"""
    # İlk olarak theme_templates koleksiyonunda kontrol et
    template_ref = db.collection('theme_templates').document(template_id).get()
    
    if template_ref.exists:
        # Tema şablonu ise
        template = ThemeTemplate.from_dict(template_ref.to_dict(), template_id)
        template_type = 'theme'
        
        theme_ref = db.collection('themes').document(template.theme_id).get()
        if not theme_ref.exists:
            flash('Tema bulunamadı', 'error')
            return redirect(url_for('themes.index'))
            
        theme = Theme.from_dict(theme_ref.to_dict(), theme_ref.id)
        
        # Kullanılabilir komponentleri getir
        components_ref = db.collection('theme_components').where('theme_id', '==', theme.id).stream()
        components = [ThemeComponent(**doc.to_dict(), id=doc.id) for doc in components_ref]
        
        # Genel komponentleri getir (tema bağımsız)
        general_components_ref = db.collection('theme_components').where('is_global', '==', True).stream()
        general_components = [ThemeComponent(**doc.to_dict(), id=doc.id) for doc in general_components_ref]
        
        # Tüm komponentleri birleştir
        all_components = components + general_components
    else:
        # Sayfa şablonu mu kontrol et
        page_template_ref = db.collection('page_templates').document(template_id).get()
        if not page_template_ref.exists:
            flash('Şablon bulunamadı', 'error')
            return redirect(url_for('themes.index'))
            
        template = PageTemplate.from_dict(page_template_ref.to_dict(), page_template_ref.id)
        template_type = 'page'
        theme = None
        
        # Sayfa bileşenlerini getir
        components_ref = db.collection('components').stream()
        all_components = [Component(**doc.to_dict(), id=doc.id) for doc in components_ref]
    
    # HTML içeriği al
    html_content = template.html_structure
    
    # Yapılandırılmış içerik oluştur
    template_content = {
        'html': html_content,
        'css': template.content.get('css', '') if hasattr(template, 'content') else '',
        'js': template.content.get('js', '') if hasattr(template, 'content') else '',
        'layout': template.content.get('layout', []) if hasattr(template, 'content') else [],
        'components': template.content.get('components', {}) if hasattr(template, 'content') else {}
    }
    
    return render_template(
        'themes/visual_editor.html',
        template=template,
        template_type=template_type,
        theme=theme,
        components=all_components,
        template_content=template_content
    )

@themes_bp.route('/preview-theme')
@login_required
@admin_required
def preview_theme():
    """Tema önizleme sayfası"""
    theme_id = request.args.get('theme_id')
    if not theme_id:
        flash('Tema ID belirtilmedi', 'error')
        return redirect(url_for('themes.index'))

    try:
        # Temayı veritabanından al
        theme_doc = db.collection('themes').document(theme_id).get()
        if not theme_doc.exists:
            current_app.logger.error(f"Tema bulunamadı (önizleme): {theme_id}")
            flash(f'Tema bulunamadı: {theme_id}', 'error')
            return redirect(url_for('themes.index'))
        
        theme_data = theme_doc.to_dict()
        theme = Theme.from_dict(theme_data, theme_id)
        current_app.logger.info(f"Tema önizleme isteği: {theme.name} (ID: {theme_id})")
        
        # Aktif tema olarak ayarla (geçici olarak)
        current_app.config['ACTIVE_THEME'] = theme_id
        current_app.logger.debug(f"Aktif tema ayarlandı: {theme_id}")
        
        # Tema dizinlerini kontrol et
        theme_dir = os.path.join(current_app.root_path, '..', 'themes', theme_id)
        template_dir = os.path.join(theme_dir, 'templates')
        static_dir = os.path.join(theme_dir, 'static')
        css_dir = os.path.join(static_dir, 'css')
        js_dir = os.path.join(static_dir, 'js')
        img_dir = os.path.join(static_dir, 'images')
        
        # Dizinleri oluştur (yoksa)
        os.makedirs(template_dir, exist_ok=True)
        os.makedirs(static_dir, exist_ok=True)
        os.makedirs(css_dir, exist_ok=True)
        os.makedirs(js_dir, exist_ok=True)
        os.makedirs(img_dir, exist_ok=True)
        
        # Veritabanındaki tema bilgilerini güncelle
        theme_updates = {
            'template_dir': os.path.join('themes', theme_id, 'templates'),
            'static_dir': os.path.join('themes', theme_id, 'static')
        }
        db.collection('themes').document(theme_id).update(theme_updates)
        
        # Tema şablonlarını veritabanından al
        theme_templates = list(db.collection('theme_templates')
                           .where('theme_id', '==', theme_id)
                           .order_by('created_at')
                           .stream())
        templates = [doc.to_dict() for doc in theme_templates]
        
        # Kurumsal içerikleri al
        contents = list(db.collection('corporate_contents').stream())
        content_list = [doc.to_dict() for doc in contents]
        
        # Önizleme için gerekli statik dosyaların URL'lerini oluştur
        preview_vars = {
            'css_url': url_for('static', filename=f'themes/{theme_id}/static/css/style.css'),
            'js_url': url_for('static', filename=f'themes/{theme_id}/static/js/main.js') if os.path.exists(os.path.join(js_dir, 'main.js')) else None,
            'favicon_url': url_for('static', filename=f'themes/{theme_id}/static/favicon.ico') if os.path.exists(os.path.join(static_dir, 'favicon.ico')) else None
        }
        
        # Site verilerini hazırla
        site_data = {}
        site_doc = db.collection('settings').document('site').get()
        if site_doc.exists:
            site_data = site_doc.to_dict()
        
        site_vars = {
            'site_title': site_data.get('site_title', 'Web Sitesi'),
            'site_name': site_data.get('site_name', 'Web Sitesi'),
            'site_description': site_data.get('site_description', 'Bu bir web sitesidir.'),
            'site_url': site_data.get('site_url', ''),
            'site_phone': site_data.get('phone', ''),
            'site_email': site_data.get('email', ''),
            'site_address': site_data.get('address', ''),
            'site_logo': site_data.get('logo_url', ''),
            'site_favicon': site_data.get('favicon_url', ''),
            'current_year': datetime.now().year,
            'theme_id': theme_id
        }
        
        # CSS dosyasının varlığını kontrol et
        css_file = os.path.join(css_dir, 'style.css')
        if not os.path.exists(css_file):
            current_app.logger.debug(f"CSS dosyası oluşturuluyor: {css_file}")
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write("""/* Tema Stil Dosyası */
body {
  font-family: 'Segoe UI', Arial, sans-serif;
  line-height: 1.6;
  color: #333;
  margin: 0;
  padding: 0;
  background-color: #f8f9fa;
}
.container {
  width: 90%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}
header {
  background-color: #343a40;
  color: white;
  padding: 20px 0;
  margin-bottom: 30px;
}
footer {
  background-color: #343a40;
  color: white;
  text-align: center;
  padding: 20px 0;
  margin-top: 30px;
}
.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  padding: 20px;
  margin-bottom: 20px;
}
h1, h2, h3 {
  color: #333;
  margin-top: 0;
}
.preview-frame {
  width: 100%;
  height: 85vh;
  border: 1px solid #ccc;
  border-radius: 4px;
}
""")
        
        # Önizleme sayfasını göster
        return render_template('themes/preview.html', 
                               theme=theme, 
                               templates=templates, 
                               contents=content_list,
                               preview_vars=preview_vars,
                               site_vars=site_vars)
    
    except Exception as e:
        current_app.logger.error(f"Tema önizleme hatası: {str(e)}", exc_info=True)
        flash(f'Tema önizleme hatası: {str(e)}', 'error')
        return redirect(url_for('themes.index'))

@themes_bp.route('/view/<theme_id>')
@login_required
@admin_required
def view(theme_id):
    """Tema detaylarını görüntüleme"""
    theme_ref = db.collection('themes').document(theme_id).get()
    if not theme_ref.exists:
        flash('Tema bulunamadı', 'error')
        return redirect(url_for('themes.index'))
        
    theme = Theme.from_dict(theme_ref.to_dict(), theme_ref.id)
    
    return render_template('themes/view.html', theme=theme)

@themes_bp.route('/view-as-website/')
@login_required
@admin_required
def view_website_home():
    """Ana sayfa için yönlendirme"""
    theme_id = request.args.get('theme_id')
    if not theme_id:
        current_app.logger.error("view_website_home: Tema ID'si belirtilmedi")
        return render_template('themes/theme_error.html', error="Tema ID'si belirtilmedi")
    
    return redirect(url_for('themes.view_website', theme_id=theme_id))
    
@themes_bp.route('/view-as-website')
@login_required
@admin_required
def view_website():
    """Tema içeriğini website olarak görüntüler"""
    theme_id = request.args.get('theme_id')
    if not theme_id:
        current_app.logger.error("view_website: Tema ID'si belirtilmedi")
        return render_template('themes/theme_error.html', error="Tema ID'si belirtilmedi")

    current_app.logger.info(f"Tema görüntüleme isteği: {theme_id}")
    try:
        # Temayı veritabanından al
        theme_doc = db.collection('themes').document(theme_id).get()
        if not theme_doc.exists:
            current_app.logger.error(f"view_website: Tema bulunamadı: {theme_id}")
            return render_template('themes/theme_error.html', error=f"Tema bulunamadı: {theme_id}")
        
        theme_data = theme_doc.to_dict()
        current_app.logger.debug(f"Tema bulundu: {theme_data.get('name')}")
        
        # Tema dizinlerini belirle
        theme_dir = os.path.join(current_app.root_path, '..', 'themes', theme_id)
        template_dir = os.path.join(theme_dir, 'templates')
        static_dir = os.path.join(theme_dir, 'static')
        css_dir = os.path.join(static_dir, 'css')
        js_dir = os.path.join(static_dir, 'js')
        img_dir = os.path.join(static_dir, 'images')
        
        # Tema dizini yoksa oluştur
        if not os.path.exists(theme_dir):
            current_app.logger.warning(f"Tema dizini bulunamadı, oluşturuluyor: {theme_dir}")
            try:
                # Tema dizin yapısını oluştur
                os.makedirs(theme_dir, exist_ok=True)
                os.makedirs(template_dir, exist_ok=True)
                os.makedirs(static_dir, exist_ok=True)
                os.makedirs(css_dir, exist_ok=True)
                os.makedirs(js_dir, exist_ok=True)
                os.makedirs(img_dir, exist_ok=True)
                current_app.logger.info(f"Tema dizin yapısı oluşturuldu: {theme_id}")
            except Exception as e:
                current_app.logger.error(f"Tema dizin yapısı oluşturulurken hata: {str(e)}", exc_info=True)
                return render_template('themes/theme_error.html', 
                                     error=f"Tema dizini oluşturulamadı: {theme_id}", 
                                     suggestions=["Dosya sistemi izinlerini kontrol edin", 
                                                  "Temayı yeniden yüklemeyi deneyin"])
        
        # index.html şablonunu oku ve render et
        index_path = os.path.join(template_dir, 'index.html')
        if not os.path.exists(index_path):
            current_app.logger.error(f"Ana sayfa şablonu bulunamadı: {index_path}")
            return render_template('themes/theme_error.html', error=f"index.html şablonu bulunamadı: {index_path}")
        
        # Site verilerini hazırla
        site_data = {}
        site_doc = db.collection('settings').document('site').get()
        if site_doc.exists:
            site_data = site_doc.to_dict()
        
        # Sayfaya özel değişkenleri hazırla
        context = {
            'site_title': site_data.get('site_title', 'Web Sitesi'),
            'site_name': site_data.get('site_name', 'Web Sitesi'),
            'site_description': site_data.get('site_description', 'Bu bir web sitesidir.'),
            'site_url': site_data.get('site_url', ''),
            'site_phone': site_data.get('phone', ''),
            'site_email': site_data.get('email', ''),
            'site_address': site_data.get('address', ''),
            'site_logo': site_data.get('logo_url', ''),
            'current_year': datetime.now().year,
            'theme_id': theme_id,
            'page_title': 'Ana Sayfa',
            'page_name': 'home',
            'page_content': 'Bu ana sayfa içeriğidir.'
        }
        
        # Yolu düzgün oluşturulmuş sayfa linkleri
        urls = {
            'services_url': url_for('themes.view_services', theme_id=theme_id),  
            'blog_url': url_for('themes.view_blog', theme_id=theme_id),
            'about_url': url_for('themes.view_about', theme_id=theme_id),
            'events_url': url_for('themes.view_events', theme_id=theme_id),
            'contact_url': url_for('themes.view_contact', theme_id=theme_id),
            'home_url': url_for('themes.view_website', theme_id=theme_id)
        }
        
        # Context'e URL'leri ekle
        context.update(urls)
        
        # Doğrudan dosyayı yükle ve render et
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
                
            # Özel Jinja2 çevre değişkeni oluştur  
            template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(index_path)))
            template = template_env.from_string(template_content)
            
            # Şablonu render et
            rendered_content = template.render(**context)
            
            # Rendered içeriğindeki bağlantıları düzelt
            rendered_content = fix_theme_links(rendered_content, theme_id)
            
            # Tema ID'sini cookie olarak sakla
            response = Response(rendered_content)
            response.set_cookie('current_theme_id', theme_id, max_age=3600*24)  # 24 saat geçerli
            
            current_app.logger.debug(f"Tema ID: {theme_id} cookie olarak kaydedildi")
            return response
        except Exception as e:
            current_app.logger.error(f"Tema render hatası: {str(e)}", exc_info=True)
            return render_template('themes/theme_error.html', 
                                 error=f"Tema render hatası: {str(e)}", 
                                 error_details=traceback.format_exc())
        
    except Exception as e:
        current_app.logger.error(f"Tema görüntüleme hatası: {str(e)}", exc_info=True)
        return render_template('themes/theme_error.html', error=f"Tema görüntüleme hatası: {str(e)}", error_details=traceback.format_exc())

def fix_theme_links(html_content, theme_id):
    """HTML içeriğindeki bağlantıları düzelt"""
    current_app.logger.debug("HTML bağlantıları düzeltiliyor")
    
    # HTML dosya bağlantılarını düzelt
    html_content = re.sub(r'href=["\']([^"\']+\.html)["\']', 
                        lambda m: f'href="/{m.group(1)}"', 
                        html_content)
    
    # CSS bağlantılarını düzelt
    html_content = re.sub(r'href=["\']css/([^"\']+)["\']', 
                        lambda m: f'href="/css/{m.group(1)}"', 
                        html_content)
    
    # JavaScript bağlantılarını düzelt
    html_content = re.sub(r'src=["\']js/([^"\']+)["\']', 
                        lambda m: f'src="/js/{m.group(1)}"', 
                        html_content)
    
    # Resim bağlantılarını düzelt
    html_content = re.sub(r'src=["\']images/([^"\']+)["\']', 
                        lambda m: f'src="/images/{m.group(1)}"', 
                        html_content)
    
    # Resim bağlantılarında başka türler
    html_content = re.sub(r'src=["\'](.*?/images/[^"\']+)["\']', 
                        lambda m: f'src="/images/{os.path.basename(m.group(1))}"', 
                        html_content)
    
    return html_content

@themes_bp.route('/theme-page/<theme_id>/<page_name>')
@login_required
@admin_required
def theme_page(theme_id, page_name):
    """Tema içindeki bir sayfayı görüntüler"""
    current_app.logger.info(f"Tema sayfası görüntüleme isteği: tema={theme_id}, sayfa={page_name}")
    
    try:
        # Temayı veritabanından al
        theme_doc = db.collection('themes').document(theme_id).get()
        if not theme_doc.exists:
            current_app.logger.error(f"theme_page: Tema bulunamadı: {theme_id}")
            return render_template('themes/theme_error.html', error=f"Tema bulunamadı: {theme_id}")
        
        theme_data = theme_doc.to_dict()
        current_app.logger.debug(f"Tema bulundu: {theme_data.get('name')}")
        
        # Tema dizinlerini belirle
        theme_dir = os.path.join(current_app.root_path, '..', 'themes', theme_id)
        template_dir = os.path.join(theme_dir, 'templates')
        static_dir = os.path.join(theme_dir, 'static')
        
        # Sayfa template dosyasını belirle - index.html, about.html, blog.html, services.html, contact.html, events.html
        if page_name == 'home':
            page_file = 'index.html'
        else:
            page_file = f"{page_name}.html"
            
        template_file_path = os.path.join(template_dir, page_file)
        
        current_app.logger.debug(f"Aranan şablon dosyası: {template_file_path}")
        
        # Sayfa dosyası yoksa, index.html kullan ve içeriği dinamik oluştur
        if not os.path.exists(template_file_path):
            current_app.logger.warning(f"Sayfa dosyası bulunamadı: {template_file_path}, index.html kullanılıyor")
            template_file_path = os.path.join(template_dir, 'index.html')
            
            # index.html bile yoksa, oluştur
            if not os.path.exists(template_file_path):
                current_app.logger.debug(f"index.html şablonu bulunamadı, varsayılan oluşturuluyor")
                os.makedirs(template_dir, exist_ok=True)
                with open(template_file_path, 'w', encoding='utf-8') as f:
                    f.write("""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page_title }} - {{ site_title }}</title>
    <link rel="stylesheet" href="/themes/css/style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>{{ site_name }}</h1>
            <nav>
                <ul>
                    <li><a href="{{ home_url }}">Ana Sayfa</a></li>
                    <li><a href="{{ about_url }}">Hakkımızda</a></li>
                    <li><a href="{{ services_url }}">Hizmetler</a></li>
                    <li><a href="{{ blog_url }}">Blog</a></li>
                    <li><a href="{{ events_url }}">Etkinlikler</a></li>
                    <li><a href="{{ contact_url }}">İletişim</a></li>
                </ul>
            </nav>
        </div>
    </header>
    
    <main>
        <div class="container">
            <div class="card">
                <h2>{{ page_title }}</h2>
                <p>{{ page_content }}</p>
            </div>
        </div>
    </main>
    
    <footer>
        <div class="container">
            <p>&copy; {{ current_year }} - {{ site_name }}</p>
        </div>
    </footer>
</body>
</html>""")
        
        # Site verilerini hazırla
        current_app.logger.debug("Web site verileri hazırlanıyor")
        site_data = {}
        site_doc = db.collection('settings').document('site').get()
        if site_doc.exists:
            site_data = site_doc.to_dict()
        
        # Sayfa içeriğini hazırla
        page_content = ""
        page_title = page_name.capitalize()
        
        # Sayfa içeriği için veritabanını kontrol et
        if page_name == "about":
            corp_doc = db.collection('corporate_contents').where('page_type', '==', 'about').limit(1).get()
            if len(list(corp_doc)) > 0:
                page_content = corp_doc[0].to_dict().get('content', '')
                page_title = corp_doc[0].to_dict().get('title', 'Hakkımızda')
        elif page_name == "services":
            page_title = "Hizmetlerimiz"
            page_content = "<p>Firmamızın sunduğu hizmetler burada listelenecektir.</p>"
        elif page_name == "blog":
            page_title = "Blog Yazıları"
            page_content = "<p>Blog yazılarımız burada listelenecektir.</p>"
        elif page_name == "events":
            page_title = "Etkinlikler"
            page_content = "<p>Etkinliklerimiz burada listelenecektir.</p>"
        elif page_name == "contact":
            page_title = "İletişim"
            page_content = f"""
            <p><strong>Adres:</strong> {site_data.get('address', '')}</p>
            <p><strong>Telefon:</strong> {site_data.get('phone', '')}</p>
            <p><strong>E-posta:</strong> {site_data.get('email', '')}</p>
            """
        else:
            page_title = f"{page_name.capitalize()} Sayfası"
            page_content = f"<p>Bu {page_name} sayfasıdır. İçerik henüz oluşturulmamıştır.</p>"
        
        # Sayfaya özel değişkenleri hazırla
        context = {
            'site_title': site_data.get('site_title', 'Web Sitesi'),
            'site_name': site_data.get('site_name', 'Web Sitesi'),
            'site_description': site_data.get('site_description', 'Bu bir web sitesidir.'),
            'site_url': site_data.get('site_url', ''),
            'site_phone': site_data.get('phone', ''),
            'site_email': site_data.get('email', ''),
            'site_address': site_data.get('address', ''),
            'site_logo': site_data.get('logo_url', ''),
            'site_favicon': site_data.get('favicon_url', ''),
            'current_year': datetime.now().year,
            'theme_id': theme_id,
            'page_title': page_title,
            'page_name': page_name,
            'page_content': page_content
        }
        
        # Yolu düzgün oluşturulmuş sayfa linkleri
        urls = {
            'services_url': url_for('themes.view_services', theme_id=theme_id),  
            'blog_url': url_for('themes.view_blog', theme_id=theme_id),
            'about_url': url_for('themes.view_about', theme_id=theme_id),
            'events_url': url_for('themes.view_events', theme_id=theme_id),
            'contact_url': url_for('themes.view_contact', theme_id=theme_id),
            'home_url': url_for('themes.view_website', theme_id=theme_id)
        }
        
        # Context'e URL'leri ekle
        context.update(urls)
        
        try:
            # Doğrudan dosyayı yükle ve render et
            with open(template_file_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
                
            # Özel Jinja2 çevre değişkeni oluştur
            template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(template_file_path)))
            template = template_env.from_string(template_content)
            
            # Şablonu render et
            rendered_content = template.render(**context)
            
            # Rendered içeriğindeki bağlantıları düzelt
            rendered_content = fix_theme_links(rendered_content, theme_id)
            
            # Tema ID'sini cookie olarak sakla
            response = Response(rendered_content)
            response.set_cookie('current_theme_id', theme_id, max_age=3600*24)  # 24 saat geçerli
            
            return response
            
        except Exception as e:
            current_app.logger.error(f"Şablon render hatası: {str(e)}", exc_info=True)
            return render_template('themes/theme_error.html', 
                              error=f"Şablon render hatası: {str(e)}", 
                              error_details=traceback.format_exc())
        
    except Exception as e:
        current_app.logger.error(f"Tema sayfası görüntüleme hatası: {str(e)}", exc_info=True)
        return render_template('themes/theme_error.html', error=f"Tema sayfası görüntüleme hatası: {str(e)}", error_details=traceback.format_exc())

@themes_bp.route('/update/<theme_id>', methods=['POST'])
@login_required
@admin_required
def update_theme(theme_id):
    """Tema bilgilerini günceller"""
    current_app.logger.info(f"Tema güncelleme isteği: {theme_id}")
    try:
        theme_doc = db.collection('themes').document(theme_id).get()
        if not theme_doc.exists:
            current_app.logger.error(f"Güncellenecek tema bulunamadı: {theme_id}")
            flash('Tema bulunamadı.', 'error')
            return redirect(url_for('themes.index'))
        
        # Form verilerini al
        name = request.form.get('name')
        description = request.form.get('description')
        author = request.form.get('author')
        version = request.form.get('version')
        is_active = request.form.get('is_active') == 'on'
        
        # Tema bilgilerini güncelle
        theme_data = theme_doc.to_dict()
        update_data = {
            'name': name or theme_data.get('name', ''),
            'description': description or theme_data.get('description', ''),
            'author': author or theme_data.get('author', ''),
            'version': version or theme_data.get('version', '1.0'),
            'updated_at': datetime.now()
        }
        
        # Tema aktifleştiriliyorsa, diğer tüm temaları pasifleştir
        if is_active and not theme_data.get('active', False):
            current_app.logger.info(f"Tema aktifleştiriliyor: {theme_id}")
            # Önce diğer tüm temaları pasifleştir
            themes_ref = db.collection('themes')
            active_themes = themes_ref.where('active', '==', True).stream()
            
            for active_theme in active_themes:
                if active_theme.id != theme_id:
                    themes_ref.document(active_theme.id).update({'active': False})
                    current_app.logger.debug(f"Tema pasifleştirildi: {active_theme.id}")
            
            # Bu temayı aktifleştir
            update_data['active'] = True
            
            # Tema dizinlerinin varlığını kontrol et
            template_dir = os.path.join(current_app.root_path, '..', theme_data.get('template_dir', ''))
            static_dir = os.path.join(current_app.root_path, '..', theme_data.get('static_dir', ''))
            
            if not os.path.exists(template_dir):
                current_app.logger.warning(f"Tema şablon dizini bulunamadı: {template_dir}")
                os.makedirs(template_dir, exist_ok=True)
            
            if not os.path.exists(static_dir):
                current_app.logger.warning(f"Tema statik dizini bulunamadı: {static_dir}")
                os.makedirs(static_dir, exist_ok=True)
            
            # index.html dosyasının varlığını kontrol et
            index_path = os.path.join(template_dir, 'index.html')
            if not os.path.exists(index_path):
                current_app.logger.warning(f"index.html dosyası bulunamadı: {index_path}")
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write("""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ site_title }}</title>
    <link rel="stylesheet" href="/themes/css/style.css">
</head>
<body>
    <header>
        <div class="container">
            <h1>{{ site_name }}</h1>
            <nav>
                <ul>
                    <li><a href="/themes/theme-page/{{ theme_id }}/home">Ana Sayfa</a></li>
                    <li><a href="/themes/theme-page/{{ theme_id }}/about">Hakkımızda</a></li>
                    <li><a href="/themes/theme-page/{{ theme_id }}/services">Hizmetler</a></li>
                    <li><a href="/themes/theme-page/{{ theme_id }}/blog">Blog</a></li>
                    <li><a href="/themes/theme-page/{{ theme_id }}/events">Etkinlikler</a></li>
                    <li><a href="/themes/theme-page/{{ theme_id }}/contact">İletişim</a></li>
                </ul>
            </nav>
        </div>
    </header>
    
    <main>
        <div class="container">
            <div class="card">
                <h2>Ana Sayfa</h2>
                <p>Bu, {{ site_name }} sitesinin ana sayfasıdır.</p>
                <p>{{ site_description }}</p>
            </div>
        </div>
    </main>
    
    <footer>
        <div class="container">
            <p>&copy; {{ current_year }} - {{ site_name }}</p>
        </div>
    </footer>
</body>
</html>""")
        else:
            # Eğer pasifleştiriliyorsa sadece aktif değerini güncelle
            update_data['active'] = is_active
        
        # Veritabanını güncelle
        db.collection('themes').document(theme_id).update(update_data)
        current_app.logger.info(f"Tema bilgileri güncellendi: {theme_id}, aktif={is_active}")
        
        flash('Tema bilgileri güncellendi.', 'success')
        return redirect(url_for('themes.index'))
        
    except Exception as e:
        current_app.logger.error(f"Tema güncelleme hatası: {str(e)}", exc_info=True)
        flash(f'Tema güncellenirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('themes.index'))

@themes_bp.route('/activate-cobsine')
@login_required
@admin_required
def activate_cobsine():
    """Cobsine temasını aktifleştirir (geçici test fonksiyonu)"""
    try:
        # cobsine temasını bul
        themes_ref = db.collection('themes')
        cobsine_id = None
        
        for theme in themes_ref.stream():
            theme_data = theme.to_dict()
            if 'name' in theme_data and 'cobsine' in theme_data['name'].lower():
                cobsine_id = theme.id
                break
        
        if not cobsine_id:
            # Cobsine teması bulunamadı, yeni bir ID ile Firebase'e kaydedelim
            cobsine_id = 'cobsine'
            
            # Önce diğer tüm temaları pasifleştir
            active_themes = themes_ref.where('active', '==', True).stream()
            for active_theme in active_themes:
                themes_ref.document(active_theme.id).update({'active': False})
            
            # Cobsine tema verisini oluştur
            cobsine_data = {
                'id': cobsine_id,
                'name': 'Cobsine',
                'description': 'Modern Business Bootstrap Tema',
                'version': '1.0',
                'author': 'BootstrapMade',
                'active': True,
                'created_at': datetime.now(),
                'updated_at': datetime.now(),
                'template_dir': 'themes/cobsine/templates',
                'static_dir': 'themes/cobsine/static'
            }
            
            # Veritabanına kaydet
            themes_ref.document(cobsine_id).set(cobsine_data)
            current_app.logger.info(f"Cobsine teması oluşturuldu ve aktifleştirildi: {cobsine_id}")
            
        else:
            # Önce diğer tüm temaları pasifleştir
            active_themes = themes_ref.where('active', '==', True).stream()
            for active_theme in active_themes:
                if active_theme.id != cobsine_id:
                    themes_ref.document(active_theme.id).update({'active': False})
            
            # Cobsine temasını aktifleştir
            themes_ref.document(cobsine_id).update({
                'active': True,
                'updated_at': datetime.now()
            })
            current_app.logger.info(f"Cobsine teması aktifleştirildi: {cobsine_id}")
        
        flash('Cobsine teması aktifleştirildi.', 'success')
        return redirect(url_for('themes.index'))
        
    except Exception as e:
        current_app.logger.error(f"Cobsine tema aktifleştirme hatası: {str(e)}", exc_info=True)
        flash(f'Cobsine teması aktifleştirilirken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('themes.index'))

@themes_bp.route('/view-as-website/index')
@login_required
@admin_required
def view_website_index():
    """Tema içeriğini index sayfasını görüntüler"""
    theme_id = request.args.get('theme_id')
    if not theme_id:
        current_app.logger.error("view_website_index: Tema ID'si belirtilmedi")
        return render_template('themes/theme_error.html', error="Tema ID'si belirtilmedi")
    
    # Tema dizinlerini oluştur
    theme_dir = os.path.join(current_app.root_path, '..', 'themes', theme_id)
    template_dir = os.path.join(theme_dir, 'templates')
    
    # index.html şablonunu oku
    index_path = os.path.join(template_dir, 'index.html')
    if not os.path.exists(index_path):
        current_app.logger.error(f"view_website_index: index.html şablonu bulunamadı: {index_path}")
        return render_template('themes/theme_error.html', error=f"index.html şablonu bulunamadı: {index_path}")
    
    # Site verilerini hazırla
    site_data = {}
    site_doc = db.collection('settings').document('site').get()
    if site_doc.exists:
        site_data = site_doc.to_dict()
    
    try:
        # Doğrudan dosyayı yükle ve render et
        with open(index_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Özel Jinja2 çevre değişkeni oluştur
        template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(index_path)))
        template = template_env.from_string(template_content)
        
        # Şablonu render et
        rendered_content = template.render(
            site_title=site_data.get('site_title', 'Web Sitesi'),
            site_name=site_data.get('site_name', 'Web Sitesi'),
            theme_id=theme_id
        )
        
        return rendered_content
    except Exception as e:
        current_app.logger.error(f"Tema render hatası: {str(e)}", exc_info=True)
        return render_template('themes/theme_error.html', 
                              error=f"Tema render hatası: {str(e)}", 
                              error_details=traceback.format_exc())

@themes_bp.route('/view-as-website/about')
@login_required
@admin_required
def view_website_about():
    """Tema içeriğinin about sayfasını görüntüler"""
    theme_id = request.args.get('theme_id')
    if not theme_id:
        current_app.logger.error("view_website_about: Tema ID'si belirtilmedi")
        return render_template('themes/theme_error.html', error="Tema ID'si belirtilmedi")
    
    # Tema dizinlerini oluştur
    theme_dir = os.path.join(current_app.root_path, '..', 'themes', theme_id)
    template_dir = os.path.join(theme_dir, 'templates')
    
    # about.html şablonunu oku
    about_path = os.path.join(template_dir, 'about.html')
    if not os.path.exists(about_path):
        current_app.logger.error(f"view_website_about: about.html şablonu bulunamadı: {about_path}")
        return render_template('themes/theme_error.html', error=f"about.html şablonu bulunamadı: {about_path}")
    
    # Site verilerini hazırla
    site_data = {}
    site_doc = db.collection('settings').document('site').get()
    if site_doc.exists:
        site_data = site_doc.to_dict()
    
    try:
        # Doğrudan dosyayı yükle ve render et
        with open(about_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Özel Jinja2 çevre değişkeni oluştur
        template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(about_path)))
        template = template_env.from_string(template_content)
        
        # Şablonu render et
        rendered_content = template.render(
            site_title=site_data.get('site_title', 'Web Sitesi'),
            site_name=site_data.get('site_name', 'Web Sitesi'),
            theme_id=theme_id
        )
        
        return rendered_content
    except Exception as e:
        current_app.logger.error(f"Tema render hatası: {str(e)}", exc_info=True)
        return render_template('themes/theme_error.html', 
                             error=f"Tema render hatası: {str(e)}", 
                             error_details=traceback.format_exc())

@themes_bp.route('/view-as-website/services')
@login_required
@admin_required
def view_website_services():
    """Tema içeriğinin services sayfasını görüntüler"""
    theme_id = request.args.get('theme_id')
    if not theme_id:
        current_app.logger.error("view_website_services: Tema ID'si belirtilmedi")
        return render_template('themes/theme_error.html', error="Tema ID'si belirtilmedi")
    
    # Tema dizinlerini oluştur
    theme_dir = os.path.join(current_app.root_path, '..', 'themes', theme_id)
    template_dir = os.path.join(theme_dir, 'templates')
    
    # services.html şablonunu oku
    services_path = os.path.join(template_dir, 'services.html')
    if not os.path.exists(services_path):
        current_app.logger.error(f"view_website_services: services.html şablonu bulunamadı: {services_path}")
        return render_template('themes/theme_error.html', error=f"services.html şablonu bulunamadı: {services_path}")
    
    # Site verilerini hazırla
    site_data = {}
    site_doc = db.collection('settings').document('site').get()
    if site_doc.exists:
        site_data = site_doc.to_dict()
    
    try:
        # Doğrudan dosyayı yükle ve render et
        with open(services_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Özel Jinja2 çevre değişkeni oluştur
        template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(services_path)))
        template = template_env.from_string(template_content)
        
        # Şablonu render et
        rendered_content = template.render(
            site_title=site_data.get('site_title', 'Web Sitesi'),
            site_name=site_data.get('site_name', 'Web Sitesi'),
            theme_id=theme_id
        )
        
        return rendered_content
    except Exception as e:
        current_app.logger.error(f"Tema render hatası: {str(e)}", exc_info=True)
        return render_template('themes/theme_error.html', 
                             error=f"Tema render hatası: {str(e)}", 
                             error_details=traceback.format_exc())

@themes_bp.route('/view-as-website/blog')
@login_required
@admin_required
def view_website_blog():
    """Tema içeriğinin blog sayfasını görüntüler"""
    theme_id = request.args.get('theme_id')
    if not theme_id:
        current_app.logger.error("view_website_blog: Tema ID'si belirtilmedi")
        return render_template('themes/theme_error.html', error="Tema ID'si belirtilmedi")
    
    # Tema dizinlerini oluştur
    theme_dir = os.path.join(current_app.root_path, '..', 'themes', theme_id)
    template_dir = os.path.join(theme_dir, 'templates')
    
    # blog.html şablonunu oku
    blog_path = os.path.join(template_dir, 'blog.html')
    if not os.path.exists(blog_path):
        current_app.logger.error(f"view_website_blog: blog.html şablonu bulunamadı: {blog_path}")
        return render_template('themes/theme_error.html', error=f"blog.html şablonu bulunamadı: {blog_path}")
    
    # Site verilerini hazırla
    site_data = {}
    site_doc = db.collection('settings').document('site').get()
    if site_doc.exists:
        site_data = site_doc.to_dict()
    
    try:
        # Doğrudan dosyayı yükle ve render et
        with open(blog_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Özel Jinja2 çevre değişkeni oluştur
        template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(blog_path)))
        template = template_env.from_string(template_content)
        
        # Şablonu render et
        rendered_content = template.render(
            site_title=site_data.get('site_title', 'Web Sitesi'),
            site_name=site_data.get('site_name', 'Web Sitesi'),
            theme_id=theme_id
        )
        
        return rendered_content
    except Exception as e:
        current_app.logger.error(f"Tema render hatası: {str(e)}", exc_info=True)
        return render_template('themes/theme_error.html', 
                             error=f"Tema render hatası: {str(e)}", 
                             error_details=traceback.format_exc())

@themes_bp.route('/view-as-website/events')
@login_required
@admin_required
def view_website_events():
    """Tema içeriğinin events sayfasını görüntüler"""
    theme_id = request.args.get('theme_id')
    if not theme_id:
        current_app.logger.error("view_website_events: Tema ID'si belirtilmedi")
        return render_template('themes/theme_error.html', error="Tema ID'si belirtilmedi")
    
    # Tema dizinlerini oluştur
    theme_dir = os.path.join(current_app.root_path, '..', 'themes', theme_id)
    template_dir = os.path.join(theme_dir, 'templates')
    
    # events.html şablonunu oku
    events_path = os.path.join(template_dir, 'events.html')
    if not os.path.exists(events_path):
        current_app.logger.error(f"view_website_events: events.html şablonu bulunamadı: {events_path}")
        return render_template('themes/theme_error.html', error=f"events.html şablonu bulunamadı: {events_path}")
    
    # Site verilerini hazırla
    site_data = {}
    site_doc = db.collection('settings').document('site').get()
    if site_doc.exists:
        site_data = site_doc.to_dict()
    
    try:
        # Doğrudan dosyayı yükle ve render et
        with open(events_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Özel Jinja2 çevre değişkeni oluştur
        template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(events_path)))
        template = template_env.from_string(template_content)
        
        # Şablonu render et
        rendered_content = template.render(
            site_title=site_data.get('site_title', 'Web Sitesi'),
            site_name=site_data.get('site_name', 'Web Sitesi'),
            theme_id=theme_id
        )
        
        return rendered_content
    except Exception as e:
        current_app.logger.error(f"Tema render hatası: {str(e)}", exc_info=True)
        return render_template('themes/theme_error.html', 
                             error=f"Tema render hatası: {str(e)}", 
                             error_details=traceback.format_exc())

@themes_bp.route('/view-as-website/contact')
@login_required
@admin_required
def view_website_contact():
    """Tema içeriğinin contact sayfasını görüntüler"""
    theme_id = request.args.get('theme_id')
    if not theme_id:
        current_app.logger.error("view_website_contact: Tema ID'si belirtilmedi")
        return render_template('themes/theme_error.html', error="Tema ID'si belirtilmedi")
    
    # Tema dizinlerini oluştur
    theme_dir = os.path.join(current_app.root_path, '..', 'themes', theme_id)
    template_dir = os.path.join(theme_dir, 'templates')
    
    # contact.html şablonunu oku
    contact_path = os.path.join(template_dir, 'contact.html')
    if not os.path.exists(contact_path):
        current_app.logger.error(f"view_website_contact: contact.html şablonu bulunamadı: {contact_path}")
        return render_template('themes/theme_error.html', error=f"contact.html şablonu bulunamadı: {contact_path}")
    
    # Site verilerini hazırla
    site_data = {}
    site_doc = db.collection('settings').document('site').get()
    if site_doc.exists:
        site_data = site_doc.to_dict()
    
    try:
        # Doğrudan dosyayı yükle ve render et
        with open(contact_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
            
        # Özel Jinja2 çevre değişkeni oluştur
        template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(contact_path)))
        template = template_env.from_string(template_content)
        
        # Şablonu render et
        rendered_content = template.render(
            site_title=site_data.get('site_title', 'Web Sitesi'),
            site_name=site_data.get('site_name', 'Web Sitesi'),
            theme_id=theme_id
        )
        
        return rendered_content
    except Exception as e:
        current_app.logger.error(f"Tema render hatası: {str(e)}", exc_info=True)
        return render_template('themes/theme_error.html', 
                             error=f"Tema render hatası: {str(e)}", 
                             error_details=traceback.format_exc())

# Diğer sayfa yönlendirmeleri için yeni rotalar
@themes_bp.route('/view/<theme_id>/services')
@login_required
@admin_required
def view_services(theme_id):
    """Services sayfasına yönlendirme"""
    return redirect(url_for('themes.theme_page', theme_id=theme_id, page_name='services'))

@themes_bp.route('/view/<theme_id>/blog')
@login_required
@admin_required
def view_blog(theme_id):
    """Blog sayfasına yönlendirme"""
    return redirect(url_for('themes.theme_page', theme_id=theme_id, page_name='blog'))

@themes_bp.route('/view/<theme_id>/about')
@login_required
@admin_required
def view_about(theme_id):
    """About sayfasına yönlendirme"""
    return redirect(url_for('themes.theme_page', theme_id=theme_id, page_name='about'))

@themes_bp.route('/view/<theme_id>/events')
@login_required
@admin_required
def view_events(theme_id):
    """Events sayfasına yönlendirme"""
    return redirect(url_for('themes.theme_page', theme_id=theme_id, page_name='events'))

@themes_bp.route('/view/<theme_id>/contact')
@login_required
@admin_required
def view_contact(theme_id):
    """Contact sayfasına yönlendirme"""
    return redirect(url_for('themes.theme_page', theme_id=theme_id, page_name='contact'))