from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, IntegerField, FieldList, FormField
from wtforms.validators import DataRequired, Length, Email, Optional, URL, NumberRange

class SocialMediaForm(FlaskForm):
    """Sosyal medya linkleri için form"""
    platform = StringField('Platform', validators=[Optional()])
    url = StringField('URL', validators=[Optional(), URL(message='Geçerli bir URL giriniz.')])
    
    class Meta:
        csrf = False  # Ana formda CSRF koruması olduğu için burada gerek yok

class TeamMemberForm(FlaskForm):
    name = StringField('Ad Soyad', validators=[
        DataRequired(message='Ad Soyad zorunludur.'),
        Length(min=3, max=100, message='Ad Soyad 3-100 karakter arasında olmalıdır.')
    ])
    
    position = StringField('Pozisyon', validators=[
        DataRequired(message='Pozisyon zorunludur.'),
        Length(min=2, max=100, message='Pozisyon 2-100 karakter arasında olmalıdır.')
    ])
    
    photo_url = StringField('Fotoğraf URL', validators=[
        Optional(),
        URL(message='Geçerli bir URL giriniz.')
    ])
    
    bio = TextAreaField('Biyografi', validators=[
        Optional(),
        Length(max=1000, message='Biyografi en fazla 1000 karakter olmalıdır.')
    ])
    
    email = StringField('E-posta', validators=[
        Optional(),
        Email(message='Geçerli bir e-posta adresi giriniz.')
    ])
    
    phone = StringField('Telefon', validators=[
        Optional(),
        Length(max=20, message='Telefon numarası en fazla 20 karakter olmalıdır.')
    ])
    
    # Sosyal medya alanları
    facebook = StringField('Facebook', validators=[
        Optional(),
        URL(message='Geçerli bir URL giriniz.')
    ])
    
    twitter = StringField('Twitter', validators=[
        Optional(),
        URL(message='Geçerli bir URL giriniz.')
    ])
    
    instagram = StringField('Instagram', validators=[
        Optional(),
        URL(message='Geçerli bir URL giriniz.')
    ])
    
    linkedin = StringField('LinkedIn', validators=[
        Optional(),
        URL(message='Geçerli bir URL giriniz.')
    ])
    
    order = IntegerField('Sıralama', validators=[
        Optional(),
        NumberRange(min=0, message='Sıralama değeri 0 veya daha büyük olmalıdır.')
    ], default=0)
    
    is_active = BooleanField('Aktif', default=True) 