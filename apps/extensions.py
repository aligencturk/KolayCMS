from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_babel import Babel

# Veritabanı nesnesi
db = SQLAlchemy()

# Login manager nesnesi
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Lütfen giriş yapın.'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    from apps.models import User
    return User.query.get(int(user_id))

# Migrate nesnesi
migrate = Migrate()

# Babel nesnesi
babel = Babel() 