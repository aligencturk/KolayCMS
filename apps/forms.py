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
    
    # Footer Ayarları
    footer_bg_color = ColorField('Arkaplan Rengi', validators=[DataRequired(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Geçerli bir renk kodu giriniz (örn: #343A40)')])
    footer_text_color = ColorField('Yazı Rengi', validators=[DataRequired(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Geçerli bir renk kodu giriniz (örn: #FFFFFF)')])
    footer_link_color = ColorField('Link Rengi', validators=[DataRequired(), Regexp(r'^#[0-9A-Fa-f]{6}$', message='Geçerli bir renk kodu giriniz (örn: #FFFFFF)')])
    
    # Özel CSS ve JS
    custom_css = TextAreaField('Özel CSS')
    custom_js = TextAreaField('Özel JavaScript')
    
    submit = SubmitField('Kaydet')