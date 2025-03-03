from flask import Blueprint

templates_bp = Blueprint('templates', __name__, template_folder='templates')

from app.modules.templates.views import routes 