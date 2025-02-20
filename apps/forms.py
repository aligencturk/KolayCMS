from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, BooleanField, ColorField, SelectField
from wtforms.validators import DataRequired, Email, Length, Regexp

class ContactForm(FlaskForm):
    name = StringField('Ad Soyad', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('E-posta', validators=[DataRequired(), Email()])
    phone = StringField('Telefon', validators=[Length(max=20)])
    message = TextAreaField('Mesaj', validators=[DataRequired(), Length(min=10, max=1000)])
    submit = SubmitField('Gönder')

class ThemeSettingsForm(FlaskForm):
    # Navbar Ayarları
    navbar_bg_color = ColorField('Arkaplan Rengi', validators=[DataRequired(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Geçerli bir renk kodu giriniz (örn: #FF0000)')])
    navbar_text_color = ColorField('Yazı Rengi', validators=[DataRequired(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Geçerli bir renk kodu giriniz (örn: #000000)')])
    navbar_active_color = ColorField('Aktif Link Rengi', validators=[DataRequired(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Geçerli bir renk kodu giriniz (örn: #007BFF)')])
    navbar_hover_color = ColorField('Hover Rengi', validators=[DataRequired(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Geçerli bir renk kodu giriniz (örn: #0056B3)')])
    navbar_is_fixed = BooleanField('Sabit Navbar')
    navbar_is_transparent = BooleanField('Şeffaf Navbar')
    
    # Body Ayarları
    body_bg_color = ColorField('Arkaplan Rengi', validators=[DataRequired(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Geçerli bir renk kodu giriniz (örn: #FFFFFF)')])
    body_text_color = ColorField('Yazı Rengi', validators=[DataRequired(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Geçerli bir renk kodu giriniz (örn: #212529)')])
    body_link_color = ColorField('Link Rengi', validators=[DataRequired(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Geçerli bir renk kodu giriniz (örn: #007BFF)')])
    body_font_family = SelectField('Yazı Tipi', choices=[
        ('Poppins', 'Poppins'),
        ('Roboto', 'Roboto'),
        ('Open Sans', 'Open Sans'),
        ('Montserrat', 'Montserrat')
    ])
    body_font_size = SelectField('Yazı Boyutu', choices=[
        ('12px', 'Küçük (12px)'),
        ('14px', 'Normal (14px)'),
        ('16px', 'Büyük (16px)'),
        ('18px', 'Çok Büyük (18px)')
    ])
    
    # Banner/Slider Ayarları
    banner_bg_color = ColorField('Arkaplan Rengi')
    banner_title_color = ColorField('Başlık Rengi')
    banner_text_color = ColorField('Metin Rengi')
    banner_button_bg_color = ColorField('Buton Arkaplan Rengi')
    banner_button_text_color = ColorField('Buton Yazı Rengi')
    banner_button_hover_bg_color = ColorField('Buton Hover Arkaplan Rengi')
    banner_button_hover_text_color = ColorField('Buton Hover Yazı Rengi')
    banner_indicator_color = ColorField('Gösterge Rengi')
    banner_arrow_color = ColorField('Ok Rengi')
    
    # Hakkımızda Ayarları
    about_bg_color = ColorField('Bölüm Arkaplan Rengi')
    about_title_color = ColorField('Ana Başlık Rengi')
    about_subtitle_color = ColorField('Alt Başlık Rengi')
    about_text_color = ColorField('İçerik Metin Rengi')
    about_stats_number_color = ColorField('İstatistik Sayı Rengi')
    about_stats_text_color = ColorField('İstatistik Metin Rengi')
    about_box_bg_color = ColorField('İstatistik Kutu Arkaplan Rengi')
    about_box_border_color = ColorField('İstatistik Kutu Kenarlık Rengi')
    
    # Hizmetler Ayarları
    services_bg_color = ColorField('Bölüm Arkaplan Rengi')
    services_title_color = ColorField('Ana Başlık Rengi')
    services_subtitle_color = ColorField('Alt Başlık Rengi')
    services_card_bg_color = ColorField('Kart Arkaplan Rengi')
    services_card_border_color = ColorField('Kart Kenarlık Rengi')
    services_icon_color = ColorField('İkon Rengi')
    services_icon_bg_color = ColorField('İkon Arkaplan Rengi')
    services_card_title_color = ColorField('Kart Başlık Rengi')
    services_card_text_color = ColorField('Kart Metin Rengi')
    services_card_hover_shadow = ColorField('Kart Hover Gölge Rengi')
    
    # Blog Ayarları
    blog_bg_color = ColorField('Bölüm Arkaplan Rengi')
    blog_title_color = ColorField('Ana Başlık Rengi')
    blog_subtitle_color = ColorField('Alt Başlık Rengi')
    blog_card_bg_color = ColorField('Kart Arkaplan Rengi')
    blog_card_border_color = ColorField('Kart Kenarlık Rengi')
    blog_date_color = ColorField('Tarih Rengi')
    blog_post_title_color = ColorField('Yazı Başlık Rengi')
    blog_excerpt_color = ColorField('Özet Metin Rengi')
    blog_card_hover_shadow = ColorField('Kart Hover Gölge Rengi')
    
    # İletişim Ayarları
    contact_bg_color = ColorField('Bölüm Arkaplan Rengi')
    contact_title_color = ColorField('Ana Başlık Rengi')
    contact_subtitle_color = ColorField('Alt Başlık Rengi')
    contact_text_color = ColorField('Metin Rengi')
    contact_info_bg_color = ColorField('Bilgi Kartı Arkaplan Rengi')
    contact_info_border_color = ColorField('Bilgi Kartı Kenarlık Rengi')
    contact_info_icon_color = ColorField('Bilgi İkon Rengi')
    contact_form_bg_color = ColorField('Form Arkaplan Rengi')
    contact_form_border_color = ColorField('Form Kenarlık Rengi')
    contact_input_bg_color = ColorField('Input Arkaplan Rengi')
    contact_input_text_color = ColorField('Input Yazı Rengi')
    contact_input_border_color = ColorField('Input Kenarlık Rengi')
    contact_button_bg_color = ColorField('Buton Arkaplan Rengi')
    contact_button_text_color = ColorField('Buton Yazı Rengi')
    contact_button_hover_bg_color = ColorField('Buton Hover Arkaplan Rengi')
    contact_button_hover_text_color = ColorField('Buton Hover Yazı Rengi')
    
    # Video Ayarları
    video_bg_color = ColorField('Bölüm Arkaplan Rengi')
    video_overlay_color = ColorField('Video Overlay Rengi')
    video_title_color = ColorField('Başlık Rengi')
    video_subtitle_color = ColorField('Alt Başlık Rengi')
    video_play_button_color = ColorField('Oynat Butonu Rengi')
    video_play_button_bg_color = ColorField('Oynat Butonu Arkaplan Rengi')
    video_play_button_hover_color = ColorField('Oynat Butonu Hover Rengi')
    video_play_button_hover_bg_color = ColorField('Oynat Butonu Hover Arkaplan Rengi')
    
    # Footer Ayarları
    footer_bg_color = ColorField('Arkaplan Rengi', validators=[DataRequired(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Geçerli bir renk kodu giriniz (örn: #343A40)')])
    footer_text_color = ColorField('Yazı Rengi', validators=[DataRequired(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Geçerli bir renk kodu giriniz (örn: #FFFFFF)')])
    footer_link_color = ColorField('Link Rengi', validators=[DataRequired(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Geçerli bir renk kodu giriniz (örn: #FFFFFF)')])
    
    # Özel CSS ve JS
    custom_css = TextAreaField('Özel CSS')
    custom_js = TextAreaField('Özel JavaScript')
    
    submit = SubmitField('Kaydet')