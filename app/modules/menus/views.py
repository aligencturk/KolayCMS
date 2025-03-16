from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required
from .models import MenuModule
from app import logger

menus_bp = Blueprint('menus', __name__, url_prefix='/menus')
menu_module = MenuModule()

@menus_bp.route('/')
@login_required
async def index():
    """Menü listesi"""
    try:
        menus = await menu_module.get_all_menus()
        return render_template('menus/index.html', menus=menus)
    except Exception as e:
        logger.error(f"Menü listesi yüklenirken hata: {str(e)}")
        flash('Menüler yüklenirken bir hata oluştu.', 'error')
        return render_template('menus/index.html', menus=[])

@menus_bp.route('/create', methods=['POST'])
@login_required
async def create():
    """Yeni menü oluştur"""
    try:
        menu_data = {
            'name': request.form.get('name'),
            'location': request.form.get('location', 'header'),
            'items': []
        }
        
        menu_id = await menu_module.create_menu(menu_data)
        if menu_id:
            flash('Menü başarıyla oluşturuldu.', 'success')
        else:
            flash('Menü oluşturulurken bir hata oluştu.', 'error')
            
    except Exception as e:
        logger.error(f"Menü oluşturulurken hata: {str(e)}")
        flash('Menü oluşturulurken bir hata oluştu.', 'error')
        
    return redirect(url_for('menus.index'))

@menus_bp.route('/<menu_id>/update', methods=['POST'])
@login_required
async def update(menu_id):
    """Menü güncelle"""
    try:
        menu_data = {
            'name': request.form.get('name'),
            'location': request.form.get('location'),
            'items': request.json.get('items', [])
        }
        
        if await menu_module.update_menu(menu_id, menu_data):
            flash('Menü başarıyla güncellendi.', 'success')
        else:
            flash('Menü güncellenirken bir hata oluştu.', 'error')
            
    except Exception as e:
        logger.error(f"Menü güncellenirken hata: {str(e)}")
        flash('Menü güncellenirken bir hata oluştu.', 'error')
        
    return redirect(url_for('menus.index'))

@menus_bp.route('/<menu_id>/delete', methods=['POST'])
@login_required
async def delete(menu_id):
    """Menü sil"""
    try:
        if await menu_module.delete_menu(menu_id):
            flash('Menü başarıyla silindi.', 'success')
        else:
            flash('Menü silinirken bir hata oluştu.', 'error')
            
    except Exception as e:
        logger.error(f"Menü silinirken hata: {str(e)}")
        flash('Menü silinirken bir hata oluştu.', 'error')
        
    return redirect(url_for('menus.index')) 