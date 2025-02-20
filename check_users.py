from app import create_app
from apps.models import db, User

app = create_app()

with app.app_context():
    users = User.query.all()
    print("\nKullanıcı Listesi:")
    print("=" * 50)
    for user in users:
        print(f"Kullanıcı Adı: {user.username}")
        print(f"E-posta: {user.email}")
        print(f"Rol: {user.role}")
        print(f"Aktif: {user.is_active}")
        print("-" * 50) 