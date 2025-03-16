from app import db, logger
from flask import render_template, current_app, url_for, redirect, flash, request
from markupsafe import Markup
import os
import re
from datetime import datetime
import traceback
import sys
import time
# from bs4 import BeautifulSoup  # Bu satırı yorum haline getiriyoruz

class ThemeService:
    """Tema işlemlerini yöneten servis sınıfı"""
    
    def __init__(self, app=None):
        self.app = app
        self.active_theme = 'default'
        self.logger = logger
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        self.active_theme = app.config.get('ACTIVE_THEME', 'default')
        
        # Tema assetlerine erişmek için yardımcı fonksiyon
        @app.context_processor
        def utility_processor():
            def theme_static(filename):
                """
                Aktif temaya bağlı assetlere erişmek için yardımcı fonksiyon.
                Kullanım: {{ url_for('theme_static', filename='css/style.css') }}
                """
                try:
                    theme_path = f"themes/{self.active_theme}"
                    return url_for('static', filename=f"{theme_path}/{filename}")
                except Exception as e:
                    self.logger.error(f"Tema asset hatası: {e}")
                    # Varsayılan asset yolunu döndür
                    return url_for('static', filename=filename)
                    
            return dict(theme_static=theme_static, active_theme=self.active_theme)
    
    def set_active_theme(self, theme_name):
        """
        Aktif temayı değiştirir.
        """
        if not theme_name:
            self.logger.warning("Boş tema adı belirtildi, varsayılan tema kullanılacak.")
            theme_name = 'default'
            
        self.active_theme = theme_name
        if self.app:
            self.app.config['ACTIVE_THEME'] = theme_name
        
        self.logger.info(f"Aktif tema '{theme_name}' olarak ayarlandı.")
        return self.active_theme
    
    def get_active_theme(self):
        """
        Aktif tema adını döndürür.
        """
        return self.active_theme
    
    def theme_exists(self, theme_name):
        """
        Belirtilen temanın varlığını kontrol eder.
        """
        if not theme_name:
            return False
            
        # Tema ID'si olarak veya tema adı olarak arama yap
        theme_dir_by_name = os.path.join(self.app.static_folder, '..', 'themes', theme_name)
        theme_dir_by_id = os.path.join(self.app.static_folder, '..', 'themes', theme_name.lower())
            
        # Önce ID ile kontrol et
        result_by_id = os.path.exists(theme_dir_by_id)
        
        # Sonra isim ile kontrol et
        result_by_name = os.path.exists(theme_dir_by_name)
        
        # İkisinden biri varsa tema mevcuttur
        result = result_by_id or result_by_name
        
        if not result:
            self.logger.warning(f"Tema kontrolü: {theme_name} teması mevcut değil veya eksik dosyaları var.")
            self.logger.debug(f"Dizin kontrolleri: ID ile dizin: {os.path.exists(theme_dir_by_id)}, İsim ile dizin: {os.path.exists(theme_dir_by_name)}")
        else:
            if result_by_id:
                self.logger.debug(f"Tema ID ile bulundu: {theme_dir_by_id}")
            else:
                self.logger.debug(f"Tema isim ile bulundu: {theme_dir_by_name}")
        
        return result
        
    def render_theme_template(self, template_name, **context):
        """
        Aktif temaya göre şablonu render eder.
        """
        try:
            # Detaylı log
            debug_info = {
                'template_name': template_name,
                'context_keys': list(context.keys()),
                'active_theme': self.active_theme,
                'request_path': request.path if request else 'no_request',
                'python_version': sys.version,
                'cwd': os.getcwd()
            }
            
            self.logger.debug(f"Tema render işlemi başlatılıyor: {debug_info}")
            
            if not self.active_theme:
                self.logger.error("Aktif tema tanımlanmamış.")
                raise ValueError("Aktif tema tanımlanmamış.")
                
            self.logger.info(f"Tema render: '{template_name}' şablonu '{self.active_theme}' teması için render ediliyor.")
            
            # Tema kök dizini - tema ID'sini kullan
            theme_root_dir = os.path.join('themes', self.active_theme)
            abs_theme_root_dir = os.path.abspath(os.path.join(self.app.root_path, '..', theme_root_dir))
            
            # Eğer tema ID'si ile dizin yoksa tema adını kontrol et (geriye uyumluluk için)
            if not os.path.exists(abs_theme_root_dir):
                # Küçük harf ve tire ile tema ID'sini normalize et
                normalized_id = self.active_theme.lower().replace('_', '-').replace(' ', '-')
                alt_theme_root_dir = os.path.join('themes', normalized_id)
                abs_alt_theme_root_dir = os.path.abspath(os.path.join(self.app.root_path, '..', alt_theme_root_dir))
                
                if os.path.exists(abs_alt_theme_root_dir):
                    # Alternatif tema dizini bulundu
                    theme_root_dir = alt_theme_root_dir
                    abs_theme_root_dir = abs_alt_theme_root_dir
                    self.logger.debug(f"Tema dizini alternatif yolla bulundu: {abs_theme_root_dir}")
            
            # Ana tema dizinini oluştur
            if not os.path.exists(abs_theme_root_dir):
                self.logger.warning(f"Tema kök dizini bulunamadı: {abs_theme_root_dir}")
                os.makedirs(abs_theme_root_dir, exist_ok=True)
                self.logger.info(f"Tema kök dizini oluşturuldu: {abs_theme_root_dir}")
            
            # Tema dizinlerini kontrol et - static dizini
            static_dir = os.path.join(theme_root_dir, 'static')
            abs_static_dir = os.path.abspath(os.path.join(self.app.root_path, '..', static_dir))
            
            if not os.path.exists(abs_static_dir):
                self.logger.warning(f"Tema statik dizini bulunamadı: {abs_static_dir}")
                os.makedirs(abs_static_dir, exist_ok=True)
                self.logger.info(f"Tema statik dizini oluşturuldu: {abs_static_dir}")
                
            # CSS, JS ve img alt dizinlerini oluştur
            css_dir = os.path.join(abs_static_dir, 'css')
            js_dir = os.path.join(abs_static_dir, 'js')
            img_dir = os.path.join(abs_static_dir, 'images')
            
            os.makedirs(css_dir, exist_ok=True)
            os.makedirs(js_dir, exist_ok=True)
            os.makedirs(img_dir, exist_ok=True)
            
            # style.css dosyasını oluştur eğer yoksa
            style_css_path = os.path.join(css_dir, 'style.css')
            if not os.path.exists(style_css_path):
                try:
                    self.logger.info(f"style.css dosyası oluşturuluyor: {style_css_path}")
                    with open(style_css_path, 'w', encoding='utf-8') as f:
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
""")
                except Exception as e:
                    self.logger.error(f"style.css oluşturma hatası: {e}")
            
            # Favicon.ico dosyasını oluştur eğer yoksa
            favicon_path = os.path.join(abs_static_dir, 'favicon.ico')
            if not os.path.exists(favicon_path):
                try:
                    self.logger.info(f"favicon.ico dosyası oluşturuluyor: {favicon_path}")
                    with open(favicon_path, 'wb') as f:
                        f.write(b'')
                except Exception as e:
                    self.logger.error(f"favicon.ico oluşturma hatası: {e}")
                
            # Tema şablon dizini
            theme_template_dir = os.path.join(theme_root_dir, 'templates')
            
            # Tema şablon dizini kontrol
            abs_template_dir = os.path.abspath(os.path.join(self.app.root_path, '..', theme_template_dir))
            if not os.path.exists(abs_template_dir):
                self.logger.warning(f"Tema şablon dizini bulunamadı: {abs_template_dir}")
                os.makedirs(abs_template_dir, exist_ok=True)
                self.logger.info(f"Tema şablon dizini oluşturuldu: {abs_template_dir}")
            
            # Tema şablon dosyası
            theme_template_path = os.path.join(theme_template_dir, template_name)
            abs_template_path = os.path.join(abs_template_dir, template_name)
            
            # Tema şablon dosyası kontrol
            if not os.path.exists(abs_template_path):
                self.logger.warning(f"Tema şablon dosyası bulunamadı: {abs_template_path}")
                
                # Eğer index.html yoksa basit bir dosya oluştur
                if template_name == 'index.html':
                    self.logger.info(f"index.html dosyası oluşturuluyor: {abs_template_path}")
                    with open(abs_template_path, 'w', encoding='utf-8') as f:
                        f.write(f"""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ site_title|default('KolayCMS') }}</title>
    <link rel="icon" href="{{ url_for('static', filename='themes/{self.active_theme}/static/favicon.ico') }}" type="image/x-icon">
    <link rel="stylesheet" href="{{ url_for('static', filename='themes/{self.active_theme}/static/css/style.css') }}">
    <meta name="csrf-token" content="{{ csrf_token }}">
    <style>
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f4f6f8; color: #333; }}
        .container {{ max-width: 1200px; margin: 0 auto; padding: 20px; }}
        header {{ background-color: #343a40; color: white; padding: 20px; text-align: center; margin-bottom: 20px; }}
        main {{ padding: 20px; }}
        .card {{ background-color: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }}
        footer {{ background-color: #343a40; color: white; padding: 20px; text-align: center; margin-top: 20px; }}
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>{{ site_name|default('KolayCMS') }}</h1>
        </div>
    </header>
    
    <main>
        <div class="container">
            <div class="card">
                <h2>Ana Sayfa</h2>
                <p>Bu, {{ site_name|default('KolayCMS') }} sitesinin ana sayfasıdır.</p>
                <p>{{ site_description|default('Bu sayfa otomatik oluşturulmuştur.') }}</p>
            </div>
            
            <div class="card">
                <h2>İletişim</h2>
                <p>Telefon: {{ site_phone|default('0123456789') }}<br>
                E-posta: {{ site_email|default('info@ornek.com') }}</p>
            </div>
        </div>
    </main>
    
    <footer>
        <div class="container">
            <p>&copy; {{ current_year|default('2023') }} {{ site_name|default('KolayCMS') }}</p>
        </div>
    </footer>
</body>
</html>""")
            
            # Şablon dosyası güncel mi kontrol et
            template_modified = False
            try:
                if os.path.exists(abs_template_path):
                    # Şablonu güncel durumunu denetle
                    template_mtime = os.path.getmtime(abs_template_path)
                    current_time = time.time()
                    # Eğer şablon 10 dakikadan daha eskiyse ve içeriğinde eksik veya hata olma ihtimali varsa
                    if (current_time - template_mtime) > 600:  # 10 dakika
                        with open(abs_template_path, 'r', encoding='utf-8') as f:
                            template_content = f.read()
                            # Şablonda basic kontroller
                            if len(template_content) < 50 or "<!DOCTYPE html>" not in template_content:
                                self.logger.warning(f"Şablon içeriği geçersiz görünüyor, yeniden oluşturuluyor: {abs_template_path}")
                                template_modified = True
            except Exception as check_error:
                self.logger.error(f"Şablon dosyası kontrol hatası: {check_error}")
                template_modified = True
            
            # Tema şablon dosyasının varlığını kontrol et
            self.logger.debug(f"Şablon dosyasını kontrol: {theme_template_path}")
            try:
                # Jinja2 şablonunu kontrol et
                try:
                    current_app.jinja_env.loader.get_source(current_app.jinja_env, theme_template_path)
                    self.logger.debug(f"Jinja2 şablonu mevcut: {theme_template_path}")
                except Exception as jinja_error:
                    self.logger.error(f"Jinja2 şablonu yüklenemedi: {jinja_error}")
                    
                    # Doğrudan dosya işlemleriyle şablonu kontrol et
                    if os.path.exists(abs_template_path):
                        with open(abs_template_path, 'r', encoding='utf-8') as f:
                            template_content = f.read()
                            self.logger.debug(f"Şablon dosyası mevcut ve içeriği {len(template_content)} karakter.")
                    else:
                        raise FileNotFoundError(f"'{template_name}' şablonu '{self.active_theme}' teması için bulunamadı.")
            except Exception as e:
                self.logger.error(f"Şablon bulunamadı veya erişilemedi: {e}")
                raise FileNotFoundError(f"'{template_name}' şablonu '{self.active_theme}' teması için bulunamadı veya erişilemedi: {e}")
            
            # Context'e tema ID'sini ekle
            if 'theme_id' not in context:
                context['theme_id'] = self.active_theme
            
            # Şablonu render et
            try:
                html_content = render_template(theme_template_path, **context)
            except Exception as render_error:
                self.logger.error(f"Şablon render hatası: {render_error}")
                
                # İçeriği doğrudan dosyadan oku ve basit bir HTML oluştur
                try:
                    with open(abs_template_path, 'r', encoding='utf-8') as f:
                        template_content = f.read()
                        
                    # Basit değişken değiştirme işlemi
                    for key, value in context.items():
                        if isinstance(value, str):
                            template_content = template_content.replace("{{ " + key + " }}", value)
                            
                    html_content = template_content
                except Exception as direct_error:
                    self.logger.error(f"Doğrudan dosya okuma hatası: {direct_error}")
                    raise ValueError(f"Şablonu render etme hatası ve alternatif çözüm başarısız: {str(render_error)}")
            
            # Dosya yollarını düzelt
            html_content = self.fix_asset_paths(html_content)
            
            return Markup(html_content)
            
        except UnicodeDecodeError as e:
            error_details = traceback.format_exc()
            self.logger.error(f"Unicode hata: Şablon dosyası kodlama sorunu. Hata: {e}\n{error_details}")
            raise ValueError(f"Şablon kodlama hatası: {str(e)}")
        except PermissionError as e:
            error_details = traceback.format_exc()
            self.logger.error(f"İzin hatası: Şablon dosyası erişim izni reddedildi. Hata: {e}\n{error_details}")
            raise ValueError(f"Şablon dosyasına erişim izni reddedildi: {str(e)}")
        except FileNotFoundError as e:
            error_details = traceback.format_exc()
            self.logger.error(f"Dosya bulunamadı hatası: {str(e)}\n{error_details}")
            raise ValueError(f"Şablon dosyası bulunamadı: {str(e)}")
        except Exception as e:
            error_details = traceback.format_exc()
            self.logger.error(f"Tema render hatası: {str(e)}\n{error_details}")
            raise ValueError(f"Tema render hatası: {str(e)}")
    
    def fix_asset_paths(self, content):
        """
        HTML içeriğindeki asset yollarını düzeltir.
        """
        if not content:
            self.logger.warning("fix_asset_paths: İçerik boş, düzeltme yapılmıyor.")
            return content
            
        if not self.active_theme:
            self.logger.warning("fix_asset_paths: Aktif tema tanımlanmamış, düzeltme yapılmıyor.")
            return content
            
        try:
            self.logger.debug(f"Asset yolları düzeltiliyor: {self.active_theme} teması için, içerik uzunluğu: {len(content)}")
            
            # JS hata yakalama kodunu ekle
            error_handler_js = """
            <script>
            // Global hata yakalayıcı
            window.onerror = function(message, source, lineno, colno, error) {
                console.error("JS Hatası yakalandı:", message, "Kaynak:", source, "Satır:", lineno);
                return true; // Varsayılan hata işlemesini engeller
            };
            </script>
            """
            
            # Favicon.ico dosyasını oluştur eğer yoksa
            favicon_path = os.path.join(self.app.static_folder, '..', 'themes', self.active_theme, 'static', 'favicon.ico')
            if not os.path.exists(favicon_path):
                try:
                    self.logger.info(f"favicon.ico dosyası oluşturuluyor: {favicon_path}")
                    os.makedirs(os.path.dirname(favicon_path), exist_ok=True)
                    with open(favicon_path, 'wb') as f:
                        f.write(b'')
                except Exception as e:
                    self.logger.error(f"favicon.ico oluşturma hatası: {e}")
            
            # Content içinde <head> etiketi varsa JS hata yakalayıcıyı ekle
            head_pos = content.find('</head>')
            if head_pos > 0:
                content = content[:head_pos] + error_handler_js + content[head_pos:]
            else:
                content = error_handler_js + content
            
            # CSS yollarını düzelt
            content = re.sub(r'href=["\'](?!https?://|//|#|mailto:|tel:)([^"\']+\.css)["\']', 
                          r'href="{{ url_for(\'theme_static\', filename=\'\1\') }}"', content)
            
            # JS yollarını düzelt
            content = re.sub(r'src=["\'](?!https?://|//|#|data:)([^"\']+\.js)["\']', 
                          r'src="{{ url_for(\'theme_static\', filename=\'\1\') }}"', content)
            
            # Resim yollarını düzelt
            content = re.sub(r'src=["\'](?!https?://|//|#|data:)([^"\']+\.(png|jpg|jpeg|gif|svg|webp))["\']', 
                          r'src="{{ url_for(\'theme_static\', filename=\'\1\') }}"', content)
            
            # Favicon yolunu düzelt
            content = re.sub(r'href=["\'](?!https?://|//|#)([^"\']+\.(ico|png))["\'](\s+rel=["\'](?:shortcut\s+)?icon["\'])', 
                          r'href="{{ url_for(\'theme_static\', filename=\'\1\') }}"\3', content)
            
            # Link yollarını düzelt
            content = re.sub(r'href=["\'](?!https?://|//|#|mailto:|tel:|{{ url_for)([^"\']+\.html)["\']', 
                          r'href="{{ url_for(\'page\', slug=\'\1\') }}"', content)
            
            # HTTP linklerini uyarı olarak işaretle
            http_links = re.findall(r'(https?://[^"\']+)', content)
            if http_links:
                self.logger.warning(f"HTTP bağlantıları tespit edildi ({len(http_links)}). Güvenlik için HTTPS kullanılması önerilir.")
            
            self.logger.debug(f"Asset yolları düzeltildi: İçerik uzunluğu: {len(content)}")
            return content
            
        except Exception as e:
            self.logger.error(f"Asset yolları düzeltme hatası: {e}")
            return content  # Hata durumunda orijinal içeriği döndür 
    
    def _ensure_theme_directories(self, theme_id):
        """
        Tema için gerekli dizinleri oluşturur
        """
        if not theme_id:
            self.logger.error("Tema ID'si belirtilmedi, dizinler oluşturulamıyor.")
            return False
            
        try:
            # Tema ID'sini kullanarak ana dizinleri oluştur
            theme_path = os.path.join(self.app.root_path, '..', 'themes', theme_id)
            template_dir = os.path.join(theme_path, 'templates')
            static_dir = os.path.join(theme_path, 'static')
            
            # Alt dizinleri belirle
            css_dir = os.path.join(static_dir, 'css')
            js_dir = os.path.join(static_dir, 'js')
            img_dir = os.path.join(static_dir, 'images')
            
            # Tüm dizinleri oluştur
            for directory in [theme_path, template_dir, static_dir, css_dir, js_dir, img_dir]:
                if not os.path.exists(directory):
                    self.logger.info(f"Tema dizini oluşturuluyor: {directory}")
                    os.makedirs(directory, exist_ok=True)
            
            # CSS dosyasını oluştur
            css_file = os.path.join(css_dir, 'style.css')
            if not os.path.exists(css_file):
                self.logger.info(f"CSS dosyası oluşturuluyor: {css_file}")
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
""")
            
            # index.html şablonunu oluştur
            index_path = os.path.join(template_dir, 'index.html')
            if not os.path.exists(index_path):
                self.logger.info(f"index.html şablonu oluşturuluyor: {index_path}")
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write("""<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ site_title|default('KolayCMS') }}</title>
    <link rel="stylesheet" href="/static/themes/{{ theme_id }}/static/css/style.css">
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
        }
        header {
            background-color: #343a40;
            color: white;
            padding: 1rem 0;
            text-align: center;
        }
        .container {
            width: 90%;
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
        }
        main {
            padding: 2rem 0;
        }
        .card {
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
        }
        h1, h2 {
            color: #333;
        }
        footer {
            background-color: #343a40;
            color: white;
            text-align: center;
            padding: 1rem 0;
            margin-top: 2rem;
        }
    </style>
</head>
<body>
    <header>
        <div class="container">
            <h1>{{ site_name|default('KolayCMS') }}</h1>
        </div>
    </header>
    
    <main>
        <div class="container">
            <div class="card">
                <h2>Ana Sayfa</h2>
                <p>Bu, {{ site_name|default('KolayCMS') }} sitesinin ana sayfasıdır.</p>
                <p>{{ site_description|default('Bu sayfa otomatik oluşturulmuştur.') }}</p>
            </div>
            
            <div class="card">
                <h2>İletişim</h2>
                <p>Telefon: {{ site_phone|default('0123456789') }}<br>
                E-posta: {{ site_email|default('info@ornek.com') }}</p>
            </div>
        </div>
    </main>
    
    <footer>
        <div class="container">
            <p>&copy; {{ current_year|default('2023') }} {{ site_name|default('KolayCMS') }}</p>
        </div>
    </footer>
</body>
</html>""")
            
            # Temanın veritabanındaki dizin yollarını güncelle
            try:
                theme_doc = db.collection('themes').document(theme_id).get()
                if theme_doc.exists:
                    theme_updates = {
                        'template_dir': os.path.join('themes', theme_id, 'templates'),
                        'static_dir': os.path.join('themes', theme_id, 'static')
                    }
                    db.collection('themes').document(theme_id).update(theme_updates)
                    self.logger.debug(f"Tema veritabanı yolları güncellendi: {theme_updates}")
            except Exception as e:
                self.logger.error(f"Tema veritabanı güncelleme hatası: {str(e)}")
                
            return True
        except Exception as e:
            self.logger.error(f"Tema dizinleri oluşturma hatası: {str(e)}", exc_info=True)
            return False