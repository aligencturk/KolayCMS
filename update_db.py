from app import create_app, db
import sqlalchemy as sa

app = create_app()
with app.app_context():
    with open('add_is_active_columns.sql', 'r') as f:
        sql = f.read()
        db.session.execute(sa.text(sql))
        db.session.commit()
    print("Veritabanı başarıyla güncellendi!") 