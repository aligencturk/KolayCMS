from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.modules.reports.models import ReportModule
from app.utils.validators import ValidationError
from app.forms.report_form import ReportForm

reports_bp = Blueprint('reports', __name__)
report_module = ReportModule()

@reports_bp.route('/')
@login_required
def index():
    """Rapor listesi sayfası"""
    page = request.args.get('page', 1, type=int)
    per_page = 10
    search_query = request.args.get('q', '')
    category = request.args.get('category', '')
    
    # Raporları getir
    if search_query:
        reports = report_module.search_reports(search_query, limit=per_page)
    elif category:
        reports = report_module.get_by_category(category, limit=per_page)
    else:
        reports = report_module.list(limit=per_page)
    
    # Kategorileri getir (benzersiz)
    all_reports = report_module.list(limit=100)
    categories = list(set(report.get('category', '') for report in all_reports if report.get('category')))
    
    return render_template('reports/index.html', 
                          reports=reports, 
                          categories=categories,
                          search_query=search_query,
                          selected_category=category)

@reports_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Yeni rapor oluşturma sayfası"""
    form = ReportForm()
    
    # Kategorileri getir (benzersiz)
    all_reports = report_module.list(limit=100)
    categories = list(set(report.get('category', '') for report in all_reports if report.get('category')))
    form.category.choices = [(c, c) for c in categories] + [('other', 'Diğer')]
    
    if form.validate_on_submit():
        try:
            # Kategori "Diğer" seçildiyse, yeni kategori kullan
            category = form.new_category.data if form.category.data == 'other' else form.category.data
            
            # Rapor verilerini hazırla
            tags = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
            
            # Raporu oluştur
            report_id = report_module.create_report(
                title=form.title.data,
                content=form.content.data,
                category=category,
                author_id=current_user.id,
                is_published=form.is_published.data,
                tags=tags,
                file_url=form.file_url.data
            )
            
            if report_id:
                flash('Rapor başarıyla oluşturuldu.', 'success')
                return redirect(url_for('reports.index'))
            else:
                flash('Rapor oluşturulurken bir hata oluştu.', 'error')
        
        except ValidationError as e:
            flash(str(e), 'error')
    
    return render_template('reports/form.html', form=form)

@reports_bp.route('/<report_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(report_id):
    """Rapor düzenleme sayfası"""
    # Raporu getir
    report = report_module.get(report_id)
    if not report:
        flash('Rapor bulunamadı.', 'error')
        return redirect(url_for('reports.index'))
    
    form = ReportForm(obj=report)
    
    # Kategorileri getir (benzersiz)
    all_reports = report_module.list(limit=100)
    categories = list(set(report.get('category', '') for report in all_reports if report.get('category')))
    form.category.choices = [(c, c) for c in categories] + [('other', 'Diğer')]
    
    # Etiketleri string'e dönüştür
    if 'tags' in report and isinstance(report['tags'], list):
        form.tags.data = ', '.join(report['tags'])
    
    if form.validate_on_submit():
        try:
            # Kategori "Diğer" seçildiyse, yeni kategori kullan
            category = form.new_category.data if form.category.data == 'other' else form.category.data
            
            # Rapor verilerini hazırla
            tags = [tag.strip() for tag in form.tags.data.split(',') if tag.strip()]
            
            # Raporu güncelle
            report_data = {
                'title': form.title.data,
                'content': form.content.data,
                'category': category,
                'is_published': form.is_published.data,
                'tags': tags,
                'file_url': form.file_url.data
            }
            
            if report_module.update_report(report_id, report_data):
                flash('Rapor başarıyla güncellendi.', 'success')
                return redirect(url_for('reports.index'))
            else:
                flash('Rapor güncellenirken bir hata oluştu.', 'error')
        
        except ValidationError as e:
            flash(str(e), 'error')
    
    return render_template('reports/form.html', form=form, report=report)

@reports_bp.route('/<report_id>/delete', methods=['DELETE'])
@login_required
def delete(report_id):
    """Rapor silme endpoint'i"""
    try:
        # Raporu getir
        report = report_module.get(report_id)
        if not report:
            return jsonify({'error': 'Rapor bulunamadı.'}), 404
        
        # Raporu sil
        if report_module.delete(report_id):
            return jsonify({'message': 'Rapor başarıyla silindi.'}), 200
        else:
            return jsonify({'error': 'Rapor silinirken bir hata oluştu.'}), 500
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/<report_id>/publish', methods=['POST'])
@login_required
def publish(report_id):
    """Raporu yayınla"""
    try:
        if report_module.publish_report(report_id):
            return jsonify({'message': 'Rapor başarıyla yayınlandı.'}), 200
        else:
            return jsonify({'error': 'Rapor yayınlanırken bir hata oluştu.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/<report_id>/unpublish', methods=['POST'])
@login_required
def unpublish(report_id):
    """Raporu yayından kaldır"""
    try:
        if report_module.unpublish_report(report_id):
            return jsonify({'message': 'Rapor başarıyla yayından kaldırıldı.'}), 200
        else:
            return jsonify({'error': 'Rapor yayından kaldırılırken bir hata oluştu.'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/<report_id>/view')
def view(report_id):
    """Rapor görüntüleme sayfası"""
    report = report_module.get(report_id)
    if not report:
        flash('Rapor bulunamadı.', 'error')
        return redirect(url_for('reports.index'))
    
    # Görüntülenme sayısını artır
    report_module.increment_view_count(report_id)
    
    return render_template('reports/view.html', report=report)
