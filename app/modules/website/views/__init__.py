from flask import Blueprint

website_bp = Blueprint('website', __name__, template_folder='../templates')

from app.modules.website.views import routes 