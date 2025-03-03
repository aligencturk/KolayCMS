from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Length, Optional, Regexp

class CorporateForm(FlaskForm):
    title = StringField('Sayfa Başlığı', validators=[
        DataRequired(message='Başlık zorunludur.'),
        Length(min=3, max=100, message='Başlık 3-100 karakter arasında olmalıdır.')
    ])
    
    slug = StringField('SEO URL', validators=[
        DataRequired(message='SEO URL zorunludur.'),
        Length(min=3, max=100, message='SEO URL 3-100 karakter arasında olmalıdır.'),
        Regexp(r'^[a-z0-9-]+$', message='SEO URL sadece küçük harf, rakam ve tire içerebilir.')
    ])
    
    content = TextAreaField('İçerik', validators=[
        DataRequired(message='İçerik zorunludur.'),
        Length(min=10, message='İçerik en az 10 karakter olmalıdır.')
    ])
    
    meta_description = TextAreaField('Meta Açıklama', validators=[
        Optional(),
        Length(max=160, message='Meta açıklama en fazla 160 karakter olmalıdır.')
    ])
    
    meta_keywords = StringField('Meta Anahtar Kelimeler', validators=[
        Optional(),
        Length(max=200, message='Meta anahtar kelimeler en fazla 200 karakter olmalıdır.')
    ])
    
    is_published = BooleanField('Yayınla', default=False) 