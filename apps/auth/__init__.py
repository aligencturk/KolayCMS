# Auth modülü için __init__.py dosyası
from flask import Blueprint

auth_bp = Blueprint('auth', __name__, 
                   template_folder='templates')

from apps.auth import views 

from apps.auth.views import auth_bp 