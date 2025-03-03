from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from app import db

class LoginForm(FlaskForm):
    """Giriş formu"""
    email = StringField('E-posta', validators=[
        DataRequired(message='E-posta adresi gerekli'),
        Email(message='Geçerli bir e-posta adresi girin')
    ])
    password = PasswordField('Şifre', validators=[
        DataRequired(message='Şifre gerekli')
    ])
    remember = BooleanField('Beni hatırla')
    submit = SubmitField('Giriş Yap')

class RegisterForm(FlaskForm):
    """Kayıt formu"""
    username = StringField('Kullanıcı Adı', validators=[
        DataRequired(message='Kullanıcı adı gerekli'),
        Length(min=3, max=50, message='Kullanıcı adı 3-50 karakter arasında olmalı')
    ])
    email = StringField('E-posta', validators=[
        DataRequired(message='E-posta adresi gerekli'),
        Email(message='Geçerli bir e-posta adresi girin')
    ])
    password = PasswordField('Şifre', validators=[
        DataRequired(message='Şifre gerekli'),
        Length(min=6, message='Şifre en az 6 karakter olmalı')
    ])
    password2 = PasswordField('Şifreyi Tekrarla', validators=[
        DataRequired(message='Şifreyi tekrar girin'),
        EqualTo('password', message='Şifreler eşleşmiyor')
    ])
    submit = SubmitField('Kayıt Ol')
    
    def validate_email(self, email):
        """E-posta adresi benzersiz olmalı"""
        users = db.collection('users').where('email', '==', email.data).get()
        if len(users) > 0:
            raise ValidationError('Bu e-posta adresi zaten kullanılıyor.')
    
    def validate_username(self, username):
        """Kullanıcı adı benzersiz olmalı"""
        users = db.collection('users').where('username', '==', username.data).get()
        if len(users) > 0:
            raise ValidationError('Bu kullanıcı adı zaten kullanılıyor.') 