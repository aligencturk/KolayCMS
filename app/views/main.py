from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.modules.reports.models import ReportModule
from app.modules.sliders.models import SliderModule
from app.modules.corporate.models import CorporateModule
from app.modules.team.models import TeamModule

# Blueprint tanımı
main_bp = Blueprint('main', __name__)

# Modülleri başlat
report_module = ReportModule()
slider_module = SliderModule()
corporate_module = CorporateModule()
team_module = TeamModule()

@main_bp.route('/')
def index():
    """Ana sayfa"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard sayfası"""
    # Modül sayılarını hesapla
    try:
        # Hata ayıklama için bir try-except bloğu ekleyelim
        report_count = len(report_module.get_all_reports())
        slider_count = len(slider_module.get_all_sliders())
        corporate_count = len(corporate_module.get_all_contents())
        team_count = len(team_module.get_active_members())
        
        return render_template('dashboard.html', 
                             title='Dashboard',
                             report_count=report_count,
                             slider_count=slider_count,
                             corporate_count=corporate_count,
                             team_count=team_count)
    except Exception as e:
        # Tam hata mesajını görmek için hatayı yakalayalım
        import traceback
        error_details = {
            'error_type': type(e).__name__,
            'error_message': str(e),
            'traceback': traceback.format_exc()
        }
        # Hata detaylarını ekranda gösterelim
        return render_template('error.html', 
                             title='Hata',
                             error=error_details)

@main_bp.route('/profile')
@login_required
def profile():
    """Kullanıcı profil sayfası"""
    return render_template('profile.html', title='Profilim')

@main_bp.app_errorhandler(404)
def page_not_found(e):
    """404 hata sayfası"""
    return render_template('errors/404.html'), 404

@main_bp.app_errorhandler(500)
def internal_server_error(e):
    """500 hata sayfası"""
    return render_template('errors/500.html'), 500 