from app import create_app, db
from models import User, SiteSettings, Page, Widget, Menu, Content, ActivityLog, Theme, Product, Category, Order

def init_db():
    app = create_app()
    with app.app_context():
        # Tüm tabloları oluştur
        db.create_all()
        
        # Varsayılan admin kullanıcısı oluştur
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
        
        # Varsayılan site ayarları oluştur
        if not SiteSettings.query.first():
            settings = SiteSettings(
                site_title='CoBsine',
                site_description='İş Ajansı ve Danışmanlık Hizmetleri',
                primary_color='#007bff',
                secondary_color='#6c757d',
                font_family='Roboto, sans-serif',
                font_size='16px',
                is_dark_mode=False
            )
            db.session.add(settings)

        # Varsayılan temayı oluştur
        if not Theme.query.first():
            theme = Theme(
                name='CoBsine Tema',
                description='İş ajansı için modern tema',
                template='',  # JavaScript kodları daha sonra eklenecek
                css='',  # CSS kodları daha sonra eklenecek
                is_active=True
            )
            db.session.add(theme)
        
        try:
            db.session.commit()
            print('Veritabanı başarıyla oluşturuldu ve varsayılan veriler eklendi.')
        except Exception as e:
            db.session.rollback()
            print(f'Hata oluştu: {str(e)}')

if __name__ == '__main__':
    init_db() 