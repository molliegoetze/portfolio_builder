from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, BooleanField, IntegerField,
                     SelectField, PasswordField, DecimalField)
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo, NumberRange

SERVICE_CATEGORIES = [
    ('', 'Select a category'),
    ('design', 'Design & Creative'),
    ('development', 'Development & IT'),
    ('marketing', 'Marketing & Business'),
    ('writing', 'Writing & Translation'),
    ('music', 'Music & Audio'),
    ('video', 'Video & Animation'),
    ('consulting', 'Consulting & Coaching'),
    ('education', 'Education & Training'),
    ('photography', 'Photography'),
    ('health', 'Health & Wellness'),
    ('legal', 'Legal & Finance'),
    ('other', 'Other'),
]

THEMES = [
    ('light', 'Light'),
    ('dark', 'Dark'),
    ('minimal', 'Minimal'),
    ('bold', 'Bold'),
]

AVAILABILITY = [
    ('available', 'Available for work'),
    ('busy', 'Busy / limited availability'),
    ('unavailable', 'Not available'),
]


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, message='Password must be at least 8 characters')])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class SiteForm(FlaskForm):
    site_title = StringField('Site Title', validators=[DataRequired(), Length(max=255)])
    subdomain = StringField('Subdomain', validators=[DataRequired(), Length(min=3, max=100)])
    theme = SelectField('Theme', choices=THEMES)
    is_published = BooleanField('Published (visible to the public)')


class ProfileForm(FlaskForm):
    display_name = StringField('Display Name', validators=[Optional(), Length(max=255)])
    headline = StringField('Headline', validators=[Optional(), Length(max=255)])
    bio = TextAreaField('Bio', validators=[Optional()])
    profile_image_url = StringField('Profile Image URL', validators=[Optional()])
    background_image_url = StringField('Background Image URL', validators=[Optional()])
    contact_email = StringField('Contact Email', validators=[Optional(), Email()])
    phone = StringField('Phone', validators=[Optional(), Length(max=50)])
    location = StringField('Location', validators=[Optional(), Length(max=255)])
    occupation = StringField('Occupation / Job Title', validators=[Optional(), Length(max=255)])
    service_category = SelectField('Service Category', choices=SERVICE_CATEGORIES)
    subcategory = StringField('Subcategory', validators=[Optional(), Length(max=100)])
    skills = StringField('Skills (comma-separated)', validators=[Optional()])
    pricing_min = DecimalField('Min Price ($)', validators=[Optional(), NumberRange(min=0)], places=2)
    pricing_max = DecimalField('Max Price ($)', validators=[Optional(), NumberRange(min=0)], places=2)
    is_remote = BooleanField('Available Remotely')
    availability_status = SelectField('Availability', choices=AVAILABILITY)
    is_searchable = BooleanField('Show in search/directory')


class LinkForm(FlaskForm):
    label = StringField('Label', validators=[DataRequired(), Length(max=100)])
    url = StringField('URL', validators=[DataRequired()])
    icon = StringField('Icon', validators=[Optional(), Length(max=50)])
    sort_order = IntegerField('Order', default=0)
    is_visible = BooleanField('Visible', default=True)


class ImageForm(FlaskForm):
    image_url = StringField('Image URL', validators=[DataRequired()])
    alt_text = StringField('Alt Text', validators=[Optional(), Length(max=255)])
    caption = TextAreaField('Caption', validators=[Optional()])
    sort_order = IntegerField('Order', default=0)
    is_visible = BooleanField('Visible', default=True)


class PortfolioItemForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[Optional()])
    image_url = StringField('Image URL', validators=[Optional()])
    project_url = StringField('Project URL', validators=[Optional()])
    github_url = StringField('GitHub URL', validators=[Optional()])
    tech_stack = StringField('Tech Stack (comma-separated)', validators=[Optional()])
    sort_order = IntegerField('Order', default=0)
    is_visible = BooleanField('Visible', default=True)
