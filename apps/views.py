from flask import render_template, send_from_directory
from apps import app
from apps.models import SiteSettings

@app.route('/')
def index():
    settings = SiteSettings.query.first()
    return render_template('main/index.html', settings=settings)

@app.route('/about')
def about():
    settings = SiteSettings.query.first()
    return render_template('main/about.html', settings=settings)

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