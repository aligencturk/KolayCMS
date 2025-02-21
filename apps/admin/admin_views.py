from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose, Admin, AdminIndexView
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField
from wtforms.validators import DataRequired
from app import db
from models import (
    User, SiteSettings, Page, Widget, Menu, Content,
    ActivityLog, Theme, Product, Category, Order
)

# Ana admin view sınıfı
class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login'))

# Template yönetimi için özel view
class TemplateManagerView(BaseView):
    @expose('/')
    @login_required
    def index(self):
        if not current_user.role == 'admin':
            flash('Bu sayfaya erişim için admin yetkisi gereklidir.', 'error')
            return redirect(url_for('auth.login'))
            
        themes = Theme.query.all()
        settings = SiteSettings.query.first()
        return render_template(
            'admin/template_manager.html',
            themes=themes,
            settings=settings
        )
    
    @expose('/save', methods=['POST'])
    @login_required
    def save_template(self):
        if not current_user.role == 'admin':
            return jsonify({'error': 'Yetkisiz erişim'}), 403
            
        try:
            theme_id = request.form.get('theme_id')
            custom_css = request.form.get('custom_css')
            custom_js = request.form.get('custom_js')
            
            theme = Theme.query.get_or_404(theme_id)
            theme.css = custom_css
            theme.template = custom_js  # JavaScript kodları için template alanını kullanıyoruz
            
            # Site ayarlarını güncelle
            settings = SiteSettings.query.first()
            if not settings:
                settings = SiteSettings()
                db.session.add(settings)
            
            settings.primary_color = request.form.get('primary_color', '#007bff')
            settings.secondary_color = request.form.get('secondary_color', '#6c757d')
            settings.font_family = request.form.get('font_family', 'Roboto')
            settings.font_size = request.form.get('font_size', '16px')
            
            db.session.commit()
            
            flash('Template başarıyla güncellendi.', 'success')
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'Template güncellenirken hata: {str(e)}')
            return jsonify({'error': str(e)}), 500
    
    @expose('/theme/<int:theme_id>')
    @login_required
    def get_theme(self, theme_id):
        if not current_user.role == 'admin':
            return jsonify({'error': 'Yetkisiz erişim'}), 403
            
        try:
            theme = Theme.query.get_or_404(theme_id)
            return jsonify({
                'css': theme.css,
                'template': theme.template
            })
        except Exception as e:
            current_app.logger.error(f'Tema bilgisi alınırken hata: {str(e)}')
            return jsonify({'error': str(e)}), 500

# Admin blueprint'i
admin_bp = Blueprint('admin', __name__)

# Temel admin view kontrolü
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        flash('Bu sayfaya erişim için admin yetkisi gereklidir.', 'error')
        return redirect(url_for('auth.login'))

# Özel widget yönetimi
class WidgetView(AdminModelView):
    column_list = ['name', 'type', 'position', 'is_active']
    form_columns = ['name', 'type', 'content', 'settings', 'position', 'is_active']
    column_searchable_list = ['name', 'type']
    column_filters = ['type', 'is_active']
    
    def on_model_change(self, form, model, is_created):
        log = ActivityLog(
            user_id=current_user.id,
            action=f'{"Created" if is_created else "Updated"} widget {model.name}',
            details=str(model.settings)
        )
        db.session.add(log)

# Sayfa yönetimi
class PageView(AdminModelView):
    column_list = ['title', 'slug', 'layout', 'is_published', 'created_at']
    form_columns = ['title', 'slug', 'content', 'layout', 'meta_description', 
                   'custom_css', 'custom_js', 'is_published']
    column_searchable_list = ['title', 'slug']
    column_filters = ['layout', 'is_published']

# Site ayarları yönetimi
class SiteSettingsView(AdminModelView):
    column_list = ['site_title', 'site_description', 'is_dark_mode']
    form_columns = ['site_title', 'site_description', 'logo_path', 'favicon_path',
                   'primary_color', 'secondary_color', 'font_family', 'font_size', 'is_dark_mode']

# Menü yönetimi
class MenuView(AdminModelView):
    column_list = ['name', 'parent_id', 'url', 'position', 'is_mega_menu']
    form_columns = ['name', 'parent_id', 'url', 'position', 'settings', 'is_mega_menu']
    column_searchable_list = ['name']
    column_filters = ['is_mega_menu']

# Tema yönetimi
class ThemeView(AdminModelView):
    column_list = ['name', 'description', 'is_active']
    form_columns = ['name', 'description', 'template', 'css', 'is_active']
    column_searchable_list = ['name']
    column_filters = ['is_active']

# Aktivite log yönetimi
class ActivityLogView(AdminModelView):
    column_list = ['user_id', 'action', 'timestamp']
    form_columns = ['user_id', 'action', 'details', 'timestamp']
    column_searchable_list = ['action']
    column_filters = ['timestamp']
    can_create = False
    can_edit = False

# E-ticaret views
class ProductView(AdminModelView):
    column_list = ['name', 'price', 'stock', 'category_id', 'is_active']
    form_columns = ['name', 'description', 'price', 'stock', 'image_path', 
                   'category_id', 'is_active']
    column_searchable_list = ['name']
    column_filters = ['category_id', 'is_active']

class CategoryView(AdminModelView):
    column_list = ['name', 'parent_id', 'description']
    form_columns = ['name', 'parent_id', 'description']
    column_searchable_list = ['name']

class OrderView(AdminModelView):
    column_list = ['id', 'user_id', 'status', 'total', 'created_at']
    form_columns = ['user_id', 'status', 'total']
    column_filters = ['status', 'created_at']

# Özel dashboard view
class DashboardView(BaseView):
    @expose('/')
    @login_required
    def index(self):
        total_pages = Page.query.count()
        total_widgets = Widget.query.count()
        total_users = User.query.count()
        recent_activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()
        
        return render_template(
            'admin/dashboard.html',
            total_pages=total_pages,
            total_widgets=total_widgets,
            total_users=total_users,
            recent_activities=recent_activities
        )

class PageForm(FlaskForm):
    title = StringField('Başlık', validators=[DataRequired()])
    menu_title = StringField('Menü Başlığı')
    slug = StringField('SEO URL', validators=[DataRequired()])
    content = TextAreaField('İçerik')
    meta_description = StringField('Meta Açıklama')
    meta_keywords = StringField('Meta Anahtar Kelimeler')
    is_published = BooleanField('Yayınla')

@admin_bp.route('/pages/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def page_edit(id):
    if not current_user.role == 'admin':
        flash('Bu sayfaya erişim için admin yetkisi gereklidir.', 'error')
        return redirect(url_for('auth.login'))
        
    page = Page.query.get_or_404(id)
    
    if request.method == 'GET':
        form = PageForm(obj=page)
    else:
        form = PageForm()
        
    if form.validate_on_submit():
        try:
            page.title = form.title.data
            page.menu_title = form.menu_title.data
            page.slug = form.slug.data
            page.content = form.content.data
            page.meta_description = form.meta_description.data
            page.meta_keywords = form.meta_keywords.data
            page.is_published = form.is_published.data
            
            db.session.commit()
            flash('Sayfa başarıyla güncellendi.', 'success')
            return redirect(url_for('admin.pages_list'))
        except Exception as e:
            db.session.rollback()
            flash('Sayfa güncellenirken bir hata oluştu.', 'error')
            current_app.logger.error(f'Sayfa güncellenirken hata: {str(e)}')
    
    return render_template('admin/pages/edit.html', page=page, form=form) 