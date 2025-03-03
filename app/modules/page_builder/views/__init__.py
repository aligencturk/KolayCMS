from flask import Blueprint

page_builder_bp = Blueprint('page_builder', __name__, template_folder='templates')

from app.modules.page_builder.views import routes 