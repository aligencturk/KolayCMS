from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, Optional

class UserForm(FlaskForm):
    """Kullanıcı oluşturma ve düzenleme formu"""
    username = StringField('Kullanıcı Adı', validators=[
        DataRequired(message='Kullanıcı adı gereklidir'),
        Length(min=3, max=50, message='Kullanıcı adı 3-50 karakter arasında olmalıdır')
    ])
    
    email = StringField('E-posta', validators=[
        DataRequired(message='E-posta adresi gereklidir'),
        Email(message='Geçerli bir e-posta adresi giriniz')
    ])
    
    role = SelectField('Rol', choices=[
        ('user', 'Kullanıcı'),
        ('editor', 'Editör'),
        ('admin', 'Yönetici')
    ], validators=[DataRequired(message='Rol seçimi gereklidir')])
    
    is_active = BooleanField('Aktif')
    
    password = PasswordField('Şifre', validators=[
        Optional(),
        Length(min=6, message='Şifre en az 6 karakter olmalıdır')
    ])
    
    confirm_password = PasswordField('Şifre (Tekrar)', validators=[
        Optional(),
        EqualTo('password', message='Şifreler eşleşmiyor')
    ])
    
    submit = SubmitField('Kaydet')
    
    def validate_password(self, field):
        # Yeni kullanıcı oluşturulurken şifre zorunlu
        if self.email.data and not self.email.object_data and not field.data:
            raise ValidationError('Yeni kullanıcı için şifre gereklidir')

class PasswordChangeForm(FlaskForm):
    """Şifre değiştirme formu"""
    current_password = PasswordField('Mevcut Şifre', validators=[
        DataRequired(message='Mevcut şifre gereklidir')
    ])
    
    new_password = PasswordField('Yeni Şifre', validators=[
        DataRequired(message='Yeni şifre gereklidir'),
        Length(min=6, message='Şifre en az 6 karakter olmalıdır')
    ])
    
    confirm_password = PasswordField('Yeni Şifre (Tekrar)', validators=[
        DataRequired(message='Şifre tekrarı gereklidir'),
        EqualTo('new_password', message='Şifreler eşleşmiyor')
    ])
    
    submit = SubmitField('Şifreyi Değiştir') 