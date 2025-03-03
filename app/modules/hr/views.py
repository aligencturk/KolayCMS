from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.modules.hr.models import HRModule

hr_bp = Blueprint('hr', __name__, url_prefix='/hr')

@hr_bp.route('/')
@login_required
def index():
    """İnsan Kaynakları ana sayfası"""
    return render_template('hr/index.html', title='İnsan Kaynakları')

@hr_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Yeni İK ilanı ekleme"""
    return render_template('hr/add.html', title='Yeni İK İlanı Ekle')

@hr_bp.route('/edit/<string:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """İK ilanı düzenleme"""
    return render_template('hr/edit.html', title='İK İlanı Düzenle', id=id)

@hr_bp.route('/delete/<string:id>', methods=['POST'])
@login_required
def delete(id):
    """İK ilanı silme"""
    flash('İlan başarıyla silindi.', 'success')
    return redirect(url_for('hr.index'))
