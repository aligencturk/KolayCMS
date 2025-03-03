from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user
from app.modules.projects.models import ProjectsModule

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')

@projects_bp.route('/')
@login_required
def index():
    """Projeler ana sayfası"""
    return render_template('projects/index.html', title='Çalışmalarımız')

@projects_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add():
    """Yeni proje ekleme"""
    return render_template('projects/add.html', title='Yeni Proje Ekle')

@projects_bp.route('/edit/<string:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Proje düzenleme"""
    return render_template('projects/edit.html', title='Proje Düzenle', id=id)

@projects_bp.route('/delete/<string:id>', methods=['POST'])
@login_required
def delete(id):
    """Proje silme"""
    flash('Proje başarıyla silindi.', 'success')
    return redirect(url_for('projects.index'))
