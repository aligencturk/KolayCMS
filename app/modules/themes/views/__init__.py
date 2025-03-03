from flask import Blueprint

themes_bp = Blueprint('themes', __name__, template_folder='templates')

from app.modules.themes.views import routes 