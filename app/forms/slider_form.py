from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, URL, Optional, NumberRange

class SliderForm(FlaskForm):
    title = StringField('Slider Başlığı', validators=[
        DataRequired(message='Başlık zorunludur.'),
        Length(min=3, max=100, message='Başlık 3-100 karakter arasında olmalıdır.')
    ])
    
    image_url = StringField('Görsel URL', validators=[
        DataRequired(message='Görsel URL zorunludur.'),
        URL(message='Geçerli bir URL giriniz.')
    ])
    
    description = TextAreaField('Açıklama', validators=[
        Optional(),
        Length(max=500, message='Açıklama en fazla 500 karakter olmalıdır.')
    ])
    
    link = StringField('Bağlantı URL', validators=[
        Optional(),
        URL(message='Geçerli bir URL giriniz.')
    ])
    
    order = IntegerField('Sıralama', validators=[
        Optional(),
        NumberRange(min=0, message='Sıralama değeri 0 veya daha büyük olmalıdır.')
    ], default=0)
    
    is_active = BooleanField('Aktif', default=True) 