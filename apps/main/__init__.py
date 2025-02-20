# Main modülü için __init__.py dosyası 
from flask import Blueprint

main_bp = Blueprint('main', __name__)

from . import views 