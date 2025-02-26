from flask import Blueprint

admin_bp = Blueprint('admin', __name__, template_folder='templates')

from . import views  # Bu import en sonda olmalı

def init_app(app):
    app.register_blueprint(admin_bp, name='admin_blueprint')
    return app 