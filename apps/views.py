from flask import render_template, send_from_directory
from apps import app
from apps.models import SiteSettings, Slider, AboutSection, Service, BlogPost, VideoSection, Page
from flask_sqlalchemy import SQLAlchemy
import json

db = SQLAlchemy()

@app.route('/')
def index():
    settings = SiteSettings.query.first()
    slides = Slider.query.filter_by(is_active=True).order_by(Slider.order.asc()).all()
    about = AboutSection.query.filter_by(is_active=True).first()
    services = Service.query.filter_by(is_active=True).order_by(Service.order.asc()).all()
    blog_posts = BlogPost.query.filter_by(is_active=True).order_by(BlogPost.created_at.desc()).limit(2).all()
    video = VideoSection.query.filter_by(is_active=True).first()
    
    return render_template('main/index.html',
                         settings=settings,
                         slides=slides,
                         about=about,
                         services=services,
                         blog_posts=blog_posts,
                         video=video)

@app.route('/about')
def about():
    settings = SiteSettings.query.first()
    page = Page.query.filter_by(slug='about').first()
    if not page:
        page = Page(
            title='Hakkımızda',
            slug='about',
            content='Hakkımızda sayfası içeriği',
            is_published=True
        )
        db.session.add(page)
        db.session.commit()
    
    about_section = AboutSection.query.first()
    if not about_section:
        about_section = AboutSection(
            title='Hakkımızda',
            subtitle='Profesyonel Çözümler',
            content='Uzun yıllara dayanan tecrübemizle müşterilerimize en iyi hizmeti sunuyoruz.',
            stats_items=json.dumps([
                {'number': '1234', 'text': 'Mutlu Müşteri'},
                {'number': '123', 'text': 'Tamamlanan Proje'},
                {'number': '12', 'text': 'Yıllık Tecrübe'}
            ]),
            is_active=True
        )
        db.session.add(about_section)
        db.session.commit()
    
    return render_template('main/about.html', settings=settings, page=page, about_section=about_section)

@app.route('/services')
def services():
    settings = SiteSettings.query.first()
    return render_template('main/services.html', settings=settings)

@app.route('/blog')
def blog():
    settings = SiteSettings.query.first()
    return render_template('main/blog.html', settings=settings)

@app.route('/contact')
def contact():
    settings = SiteSettings.query.first()
    return render_template('main/contact.html', settings=settings)

@app.route('/static/<path:filename>')
def serve_static(filename):
    if filename.endswith('.css'):
        settings = SiteSettings.query.first()
        return render_template(f'static/{filename}', settings=settings, mimetype='text/css')
    return send_from_directory('static', filename) 