import re
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User, Site, Profile
from forms import RegisterForm, LoginForm

# Create a Blueprint named 'auth' — groups all login/register/logout routes together
auth_bp = Blueprint('auth', __name__)


def _generate_subdomain(email):
    """Generate a unique subdomain from email prefix."""
    # Strip everything after '@' and remove any character that isn't a-z or 0-9
    base = re.sub(r'[^a-z0-9]', '', email.split('@')[0].lower())

    # Fallback if the email prefix produced an empty string
    if not base:
        base = 'user'

    subdomain = base
    counter = 1

    # Keep incrementing a counter (e.g. jane, jane1, jane2) until we find a subdomain not already taken
    while Site.query.filter_by(subdomain=subdomain).first():
        subdomain = f'{base}{counter}'
        counter += 1

    return subdomain


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    # If the user is already logged in, send them straight to the dashboard
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    # Create a blank registration form
    form = RegisterForm()

    if form.validate_on_submit():  # runs only on POST with valid data
        # Check whether an account with this email already exists
        if User.query.filter_by(email=form.email.data.lower()).first():
            flash('An account with that email already exists.', 'danger')
            return render_template('auth/register.html', form=form)

        # Create the User record and hash the password
        user = User(email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)

        # flush() writes to the DB within the current transaction so we can read user.id
        # without fully committing yet — needed because Site requires user_id
        db.session.flush()

        # Auto-generate a URL-safe subdomain from the email prefix (e.g. jane@... → /u/jane)
        subdomain = _generate_subdomain(form.email.data)

        # Create the Site record linked to this new user
        site = Site(
            user_id=user.id,
            site_title='My Page',
            subdomain=subdomain,
            theme='light',
            is_published=False,  # new sites start as drafts, not publicly visible
        )
        db.session.add(site)
        db.session.flush()  # flush again so we can read site.id for the Profile below

        # Create an empty Profile linked to the new site (user fills it in later)
        profile = Profile(site_id=site.id)
        db.session.add(profile)

        # Commit all three records (User, Site, Profile) to the database at once
        db.session.commit()

        # Log the new user in immediately so they land on the dashboard
        login_user(user)
        flash('Account created! Set up your page below.', 'success')
        return redirect(url_for('dashboard.site_settings'))

    # GET request — just render the empty registration form
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # Already logged in — no need to show the login page
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = LoginForm()

    if form.validate_on_submit():
        # Look up the user by email (case-insensitive via .lower())
        user = User.query.filter_by(email=form.email.data.lower()).first()

        # Verify the password hash; if both checks pass, log the user in
        if user and user.check_password(form.password.data):
            login_user(user)

            # Respect a 'next' redirect if the user was bounced here from a protected page
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))

        flash('Invalid email or password.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout', methods=['POST'])
@login_required  # only logged-in users can log out
def logout():
    logout_user()  # clears the session cookie
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
