from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.modules.services.models import ServicesModule

services_bp = Blueprint('services', __name__, url_prefix='/services')

@services_bp.route('/')
@login_required
def index():
    """Hizmetler ana sayfası"""
    return render_template('services/index.html', title='Hizmetlerimiz')

@services_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Yeni hizmet ekleme"""
    return render_template('services/add.html', title='Yeni Hizmet Ekle')

@services_bp.route('/edit/<string:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Hizmet düzenleme"""
    return render_template('services/edit.html', title='Hizmet Düzenle', id=id)

@services_bp.route('/delete/<string:id>', methods=['POST'])
@login_required
def delete(id):
    """Hizmet silme"""
    flash('Hizmet başarıyla silindi.', 'success')
    return redirect(url_for('services.index'))
