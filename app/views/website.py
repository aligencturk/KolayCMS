from flask import Blueprint, request
from app import logger
from app.services.theme_service import ThemeService

website_bp = Blueprint('website', __name__)

@website_bp.route('/')
def index():
    """Ana sayfa"""
    try:
        return ThemeService.render_theme_template('index.html')
    except Exception as e:
        logger.error(f"Ana sayfa render hatası: {str(e)}", exc_info=True)
        return render_template('errors/500.html'), 500

@website_bp.route('/<path:page>')
def page(page):
    """Diğer sayfalar"""
    try:
        return ThemeService.render_theme_template(f'{page}.html')
    except Exception as e:
        logger.error(f"Sayfa render hatası: {str(e)}", exc_info=True)
        return render_template('errors/404.html'), 404 