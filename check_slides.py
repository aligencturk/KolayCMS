import os
from flask import Flask
from apps.extensions import db
from apps.models.content_types import Slide

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "instance", "kolaycms.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    slides = Slide.query.order_by(Slide.order).all()
    print("\nSlayt Listesi:")
    print("-" * 50)
    for slide in slides:
        print(f"ID: {slide.id}")
        print(f"Başlık: {slide.title}")
        print(f"Aktif: {slide.is_active}")
        print(f"Sıra: {slide.order}")
        print(f"Resim: {slide.image_path}")
        print("-" * 50) 