from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    sites = db.relationship('Site', back_populates='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def site(self):
        return self.sites[0] if self.sites else None


class Site(db.Model):
    __tablename__ = 'sites'

    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    site_title = db.Column(db.String(255), nullable=False)
    subdomain = db.Column(db.String(100), unique=True)
    theme = db.Column(db.String(50), default='light')
    is_published = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = db.relationship('User', back_populates='sites')
    profile = db.relationship('Profile', back_populates='site', uselist=False, lazy=True)
    links = db.relationship('Link', back_populates='site', lazy=True, order_by='Link.sort_order')
    images = db.relationship('Image', back_populates='site', lazy=True, order_by='Image.sort_order')
    portfolio_items = db.relationship('PortfolioItem', back_populates='site', lazy=True, order_by='PortfolioItem.sort_order')


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.BigInteger, primary_key=True)
    site_id = db.Column(db.BigInteger, db.ForeignKey('sites.id', ondelete='CASCADE'), nullable=False, unique=True)
    display_name = db.Column(db.String(255))
    headline = db.Column(db.String(255))
    bio = db.Column(db.Text)
    profile_image_url = db.Column(db.Text)
    background_image_url = db.Column(db.Text)
    contact_email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    location = db.Column(db.String(255))
    occupation = db.Column(db.String(255))
    service_category = db.Column(db.String(100))
    subcategory = db.Column(db.String(100))
    skills = db.Column(db.Text)
    pricing_min = db.Column(db.Numeric(10, 2))
    pricing_max = db.Column(db.Numeric(10, 2))
    is_remote = db.Column(db.Boolean, default=False)
    availability_status = db.Column(db.String(50), default='available')
    is_searchable = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    site = db.relationship('Site', back_populates='profile')

    def skills_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def tech_list(self):
        return self.skills_list()


class Link(db.Model):
    __tablename__ = 'links'

    id = db.Column(db.BigInteger, primary_key=True)
    site_id = db.Column(db.BigInteger, db.ForeignKey('sites.id', ondelete='CASCADE'), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    url = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(50))
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_visible = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    site = db.relationship('Site', back_populates='links')


class Image(db.Model):
    __tablename__ = 'images'

    id = db.Column(db.BigInteger, primary_key=True)
    site_id = db.Column(db.BigInteger, db.ForeignKey('sites.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.Text, nullable=False)
    alt_text = db.Column(db.String(255))
    caption = db.Column(db.Text)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_visible = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    site = db.relationship('Site', back_populates='images')


class PortfolioItem(db.Model):
    __tablename__ = 'portfolio_items'

    id = db.Column(db.BigInteger, primary_key=True)
    site_id = db.Column(db.BigInteger, db.ForeignKey('sites.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    image_url = db.Column(db.Text)
    project_url = db.Column(db.Text)
    github_url = db.Column(db.Text)
    tech_stack = db.Column(db.Text)
    sort_order = db.Column(db.Integer, nullable=False, default=0)
    is_visible = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    site = db.relationship('Site', back_populates='portfolio_items')

    def tech_list(self):
        if not self.tech_stack:
            return []
        return [t.strip() for t in self.tech_stack.split(',') if t.strip()]
