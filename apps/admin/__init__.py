from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin', template_folder='templates')

from . import views  # Bu import en sonda olmalı

def init_app(app):
    app.register_blueprint(admin_bp)
    return app 