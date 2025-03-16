from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.models.blog import BlogPost
from app.utils.firebase import db

bp = Blueprint('blog', __name__, url_prefix='/blog')

@bp.route('/')
@login_required
def index():
    posts = []
    try:
        posts_ref = db.collection('blog_posts').stream()
        posts = [post.to_dict() for post in posts_ref]
    except Exception as e:
        flash(f'Blog yazıları yüklenirken hata oluştu: {str(e)}', 'error')
    
    return render_template('blog/index.html', posts=posts)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            flash('Başlık ve içerik alanları zorunludur.', 'error')
            return redirect(url_for('blog.create'))
        
        try:
            post = BlogPost(title=title, content=content)
            db.collection('blog_posts').add(post.to_dict())
            flash('Blog yazısı başarıyla oluşturuldu.', 'success')
            return redirect(url_for('blog.index'))
        except Exception as e:
            flash(f'Blog yazısı oluşturulurken hata oluştu: {str(e)}', 'error')
    
    return render_template('blog/create.html')

@bp.route('/<post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    post_ref = db.collection('blog_posts').document(post_id)
    post = post_ref.get()
    
    if not post.exists:
        flash('Blog yazısı bulunamadı.', 'error')
        return redirect(url_for('blog.index'))
    
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        
        if not title or not content:
            flash('Başlık ve içerik alanları zorunludur.', 'error')
            return redirect(url_for('blog.edit', post_id=post_id))
        
        try:
            post_ref.update({
                'title': title,
                'content': content
            })
            flash('Blog yazısı başarıyla güncellendi.', 'success')
            return redirect(url_for('blog.index'))
        except Exception as e:
            flash(f'Blog yazısı güncellenirken hata oluştu: {str(e)}', 'error')
    
    return render_template('blog/edit.html', post=post.to_dict()) 