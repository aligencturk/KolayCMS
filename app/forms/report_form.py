from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, URL

class ReportForm(FlaskForm):
    title = StringField('Rapor Başlığı', validators=[
        DataRequired(message='Başlık zorunludur.'),
        Length(min=3, max=100, message='Başlık 3-100 karakter arasında olmalıdır.')
    ])
    
    content = TextAreaField('Rapor İçeriği', validators=[
        DataRequired(message='İçerik zorunludur.'),
        Length(min=10, message='İçerik en az 10 karakter olmalıdır.')
    ])
    
    category = SelectField('Kategori', validators=[
        DataRequired(message='Kategori seçimi zorunludur.')
    ])
    
    new_category = StringField('Yeni Kategori', validators=[
        Optional(),
        Length(min=2, max=50, message='Kategori adı 2-50 karakter arasında olmalıdır.')
    ])
    
    tags = StringField('Etiketler (virgülle ayırın)', validators=[
        Optional(),
        Length(max=200, message='Etiketler çok uzun.')
    ])
    
    file_url = StringField('Dosya URL', validators=[
        Optional(),
        URL(message='Geçerli bir URL giriniz.')
    ])
    
    is_published = BooleanField('Yayınla', default=False) 