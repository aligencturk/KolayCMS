from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func

from app import main_bp, db, current_app
from app.models.blog_post import BlogPost

@main_bp.route('/blog')
def blog():
    """Blog sayfasını görüntüle"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 6  # Sayfa başına gösterilecek yazı sayısı
        search_query = request.args.get('q', '')
        
        # Yayınlanmış blog yazılarını getir
        query = BlogPost.query.filter_by(is_published=True)
        
        # Arama sorgusu varsa filtrele
        if search_query:
            query = query.filter(
                BlogPost.title.like(f'%{search_query}%') | 
                BlogPost.content.like(f'%{search_query}%') |
                BlogPost.excerpt.like(f'%{search_query}%')
            )
        
        blog_posts = query.order_by(BlogPost.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Son yazıları getir (sidebar için)
        recent_posts = BlogPost.query.filter_by(is_published=True) \
            .order_by(BlogPost.created_at.desc()).limit(5).all()
        
        return render_template('blog/index.html', 
                              blog_posts=blog_posts,
                              recent_posts=recent_posts,
                              search_query=search_query,
                              meta_title="Blog" + (f" - {search_query}" if search_query else ""), 
                              meta_description="Blog yazılarımız" + (f" - {search_query} ile ilgili sonuçlar" if search_query else ""))
    except Exception as e:
        current_app.logger.error(f"Blog sayfası yüklenirken hata: {str(e)}")
        flash("Blog sayfası yüklenirken bir hata oluştu.", "danger")
        return redirect(url_for('main.index'))

@main_bp.route('/blog/<slug>')
def blog_detail(slug):
    """Blog yazısı detay sayfasını görüntüle"""
    try:
        # Slug'a göre blog yazısını getir
        post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
        
        # Benzer yazıları getir (örnek olarak aynı tarihte olanlar veya rastgele birkaç yazı)
        similar_posts = BlogPost.query.filter(
            BlogPost.id != post.id, 
            BlogPost.is_published == True
        ).order_by(func.random()).limit(3).all()
        
        # Son yazıları getir (sidebar için)
        recent_posts = BlogPost.query.filter_by(is_published=True) \
            .order_by(BlogPost.created_at.desc()).limit(5).all()
        
        # Görüntülenme sayısını artır (opsiyonel)
        if hasattr(post, 'views'):
            post.views += 1
            db.session.commit()
        
        return render_template('blog/detail.html', 
                              post=post,
                              similar_posts=similar_posts,
                              recent_posts=recent_posts,
                              meta_title=post.title, 
                              meta_description=post.excerpt or post.title)
    except Exception as e:
        current_app.logger.error(f"Blog yazısı yüklenirken hata: {str(e)}")
        flash("Blog yazısı yüklenirken bir hata oluştu.", "danger")
        return redirect(url_for('main.blog')) 