from app import create_app
from apps.models.theme import Theme
from apps.extensions import db

app = create_app()

with app.app_context():
    # Mevcut temaları kontrol et
    existing_theme = Theme.query.filter_by(name='CobSin').first()
    
    if existing_theme:
        print("CobSin teması zaten mevcut.")
        
        # Temayı aktif et
        if not existing_theme.is_active:
            existing_theme.is_active = True
            
            # Var olan diğer temaları devre dışı bırak
            other_themes = Theme.query.filter(Theme.name != 'CobSin').all()
            for theme in other_themes:
                theme.is_active = False
                
            db.session.commit()
            print("CobSin teması aktif edildi.")
        else:
            print("CobSin teması zaten aktif.")
    else:
        # Yeni tema oluştur
        cobsin_theme = Theme(
            name='CobSin',
            description='Modern ve profesyonel kurumsal web sitesi teması',
            folder_name='cobsin',
            version='1.0',
            author='KolayCMS',
            screenshot_url='/static/cobsin_template/img/screenshot.jpg',
            is_active=True,
            settings={}
        )
        
        # Var olan diğer temaları devre dışı bırak
        other_themes = Theme.query.filter(Theme.name != 'CobSin').all()
        for theme in other_themes:
            theme.is_active = False
        
        # Yeni temayı kaydet
        db.session.add(cobsin_theme)
        db.session.commit()
        
        print("CobSin teması başarıyla eklendi ve aktif edildi.") 