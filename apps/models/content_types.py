from datetime import datetime
from apps.extensions import db
from slugify import slugify

class Slide(db.Model):
    __tablename__ = 'slides'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    description = db.Column(db.Text)
    image_path = db.Column(db.String(200), nullable=False)
    button_text = db.Column(db.String(50))
    button_url = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __str__(self):
        return self.title or f"Slayt #{self.id}"

class AboutSection(db.Model):
    __tablename__ = 'about_sections'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(200))
    content = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    stats_title = db.Column(db.String(200))
    stats_content = db.Column(db.Text)
    stats_items = db.Column(db.JSON)  # [{"number": "100+", "text": "Müşteri"}]
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __str__(self):
        return self.title

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Font Awesome icon ismi
    image_path = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __str__(self):
        return self.title

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    category = db.Column(db.String(100))  # web, mobile, desktop vb.
    client = db.Column(db.String(200))
    completion_date = db.Column(db.Date)
    technologies = db.Column(db.String(200))  # Virgülle ayrılmış teknolojiler
    project_url = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class TeamMember(db.Model):
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    bio = db.Column(db.Text)
    image_path = db.Column(db.String(200))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    linkedin_url = db.Column(db.String(200))
    github_url = db.Column(db.String(200))
    twitter_url = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class Testimonial(db.Model):
    __tablename__ = 'testimonials'
    
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    client_title = db.Column(db.String(100))
    client_company = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(200))
    rating = db.Column(db.Integer)  # 1-5 arası yıldız
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

class ContactInfo(db.Model):
    __tablename__ = 'contact_info'
    
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('pages.id', ondelete='CASCADE', name='fk_contact_info_page'), unique=True)
    address = db.Column(db.String(500))
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    google_maps_embed = db.Column(db.Text)
    working_hours = db.Column(db.String(200))
    facebook = db.Column(db.String(200))
    twitter = db.Column(db.String(200))
    instagram = db.Column(db.String(200))
    linkedin = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __str__(self):
        return f"Contact Info for Page {self.page_id}"

class VideoSection(db.Model):
    __tablename__ = 'video_sections'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    url = db.Column(db.String(200), nullable=False)  # YouTube, Vimeo vb. video URL'i
    thumbnail = db.Column(db.String(200))
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    def __str__(self):
        return self.title 