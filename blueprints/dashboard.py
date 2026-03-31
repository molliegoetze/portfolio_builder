from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from models import db, Site, Profile, Link, Image, PortfolioItem
from forms import SiteForm, ProfileForm, LinkForm, ImageForm, PortfolioItemForm

# Blueprint for all dashboard routes — every route here requires the user to be logged in
dashboard_bp = Blueprint('dashboard', __name__)


def _get_site_or_abort():
    """Return the current user's site, or raise a 404 if they don't have one yet."""
    site = current_user.site
    if not site:
        abort(404)
    return site


# ── Dashboard home ────────────────────────────────────────────────────────────

@dashboard_bp.route('/')
@login_required  # redirect to login if not authenticated
def index():
    site = current_user.site

    # If the user has no site yet, send them to site settings to create one
    if not site:
        return redirect(url_for('dashboard.site_settings'))

    # Render the dashboard overview with site stats and publish status
    return render_template('dashboard/index.html', site=site, profile=site.profile)


# ── Site settings ─────────────────────────────────────────────────────────────

@dashboard_bp.route('/site', methods=['GET', 'POST'])
@login_required
def site_settings():
    site = current_user.site

    # Pre-populate the form with the current site values (obj=site)
    form = SiteForm(obj=site)

    if form.validate_on_submit():  # POST with valid data
        # Normalise the subdomain to lowercase with no surrounding spaces
        new_subdomain = form.subdomain.data.lower().strip()

        # Check that the chosen subdomain isn't already used by a different site
        existing = Site.query.filter_by(subdomain=new_subdomain).first()
        if existing and (not site or existing.id != site.id):
            flash('That subdomain is already taken. Please choose another.', 'danger')
            return render_template('dashboard/site.html', form=form, site=site)

        if site:
            # Update the existing site record in place
            site.site_title  = form.site_title.data
            site.subdomain   = new_subdomain
            site.theme       = form.theme.data
            site.is_published = form.is_published.data
        else:
            # First-time setup — create the Site record
            site = Site(
                user_id=current_user.id,
                site_title=form.site_title.data,
                subdomain=new_subdomain,
                theme=form.theme.data,
                is_published=form.is_published.data,
            )
            db.session.add(site)

            # flush() lets us read site.id before the full commit so we can link the Profile
            db.session.flush()

            # Create the associated Profile record (blank — user fills it in later)
            profile = Profile(site_id=site.id)
            db.session.add(profile)

        db.session.commit()
        flash('Site settings saved.', 'success')
        return redirect(url_for('dashboard.site_settings'))

    # GET request — render the settings form
    return render_template('dashboard/site.html', form=form, site=site)


# ── Profile ───────────────────────────────────────────────────────────────────

@dashboard_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    site = _get_site_or_abort()
    p    = site.profile  # the one-to-one Profile linked to this site

    # Pre-populate the form with existing profile data
    form = ProfileForm(obj=p)

    if form.validate_on_submit():
        # populate_obj() maps every form field onto the matching attribute of the profile object
        form.populate_obj(p)
        db.session.commit()
        flash('Profile saved.', 'success')
        return redirect(url_for('dashboard.profile'))

    return render_template('dashboard/profile.html', form=form, site=site, profile=p)


# ── Links ─────────────────────────────────────────────────────────────────────

@dashboard_bp.route('/links', methods=['GET', 'POST'])
@login_required
def links():
    site = _get_site_or_abort()
    form = LinkForm()  # blank form for adding a new link

    if form.validate_on_submit():
        # Create a new Link record owned by this site
        link = Link(
            site_id=site.id,
            label=form.label.data,
            url=form.url.data,
            icon=form.icon.data,
            sort_order=form.sort_order.data or 0,  # default to 0 if not provided
            is_visible=form.is_visible.data,
        )
        db.session.add(link)
        db.session.commit()
        flash('Link added.', 'success')
        return redirect(url_for('dashboard.links'))

    # GET — render the links management page (existing links are on site.links)
    return render_template('dashboard/links.html', site=site, form=form)


@dashboard_bp.route('/links/<int:link_id>/edit', methods=['POST'])
@login_required
def edit_link(link_id):
    site = _get_site_or_abort()

    # Fetch the link, ensuring it belongs to the current user's site (prevents cross-user edits)
    link = Link.query.filter_by(id=link_id, site_id=site.id).first_or_404()
    form = LinkForm()

    if form.validate_on_submit():
        # Overwrite each field with the submitted form values
        link.label      = form.label.data
        link.url        = form.url.data
        link.icon       = form.icon.data
        link.sort_order = form.sort_order.data or 0
        link.is_visible = form.is_visible.data
        db.session.commit()
        flash('Link updated.', 'success')

    return redirect(url_for('dashboard.links'))


@dashboard_bp.route('/links/<int:link_id>/delete', methods=['POST'])
@login_required
def delete_link(link_id):
    site = _get_site_or_abort()

    # Verify ownership before deleting
    link = Link.query.filter_by(id=link_id, site_id=site.id).first_or_404()
    db.session.delete(link)
    db.session.commit()
    flash('Link deleted.', 'info')
    return redirect(url_for('dashboard.links'))


@dashboard_bp.route('/links/reorder', methods=['POST'])
@login_required
def reorder_links():
    site = _get_site_or_abort()

    # The front-end sends a list of link IDs in the new desired order
    ids = request.form.getlist('order[]')

    # Set each link's sort_order to its position in the submitted list
    for i, link_id in enumerate(ids):
        link = Link.query.filter_by(id=int(link_id), site_id=site.id).first()
        if link:
            link.sort_order = i  # i=0 is first, i=1 is second, etc.

    db.session.commit()
    return ('', 204)  # 204 No Content — success with no body (called via AJAX)


# ── Images ────────────────────────────────────────────────────────────────────

@dashboard_bp.route('/images', methods=['GET', 'POST'])
@login_required
def images():
    site = _get_site_or_abort()
    form = ImageForm()

    if form.validate_on_submit():
        # Create a new Image record linked to this site
        image = Image(
            site_id=site.id,
            image_url=form.image_url.data,
            alt_text=form.alt_text.data,
            caption=form.caption.data,
            sort_order=form.sort_order.data or 0,
            is_visible=form.is_visible.data,
        )
        db.session.add(image)
        db.session.commit()
        flash('Image added.', 'success')
        return redirect(url_for('dashboard.images'))

    return render_template('dashboard/images.html', site=site, form=form)


@dashboard_bp.route('/images/<int:image_id>/edit', methods=['POST'])
@login_required
def edit_image(image_id):
    site  = _get_site_or_abort()

    # Verify the image belongs to this user's site before editing
    image = Image.query.filter_by(id=image_id, site_id=site.id).first_or_404()
    form  = ImageForm()

    if form.validate_on_submit():
        # Update each field with the new values from the form
        image.image_url  = form.image_url.data
        image.alt_text   = form.alt_text.data
        image.caption    = form.caption.data
        image.sort_order = form.sort_order.data or 0
        image.is_visible = form.is_visible.data
        db.session.commit()
        flash('Image updated.', 'success')

    return redirect(url_for('dashboard.images'))


@dashboard_bp.route('/images/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_image(image_id):
    site  = _get_site_or_abort()
    image = Image.query.filter_by(id=image_id, site_id=site.id).first_or_404()
    db.session.delete(image)
    db.session.commit()
    flash('Image deleted.', 'info')
    return redirect(url_for('dashboard.images'))


# ── Portfolio ─────────────────────────────────────────────────────────────────

@dashboard_bp.route('/portfolio', methods=['GET', 'POST'])
@login_required
def portfolio():
    site = _get_site_or_abort()
    form = PortfolioItemForm()

    if form.validate_on_submit():
        # Create a new PortfolioItem with all fields from the form
        item = PortfolioItem(
            site_id=site.id,
            title=form.title.data,
            description=form.description.data,
            image_url=form.image_url.data,
            project_url=form.project_url.data,    # live demo link
            github_url=form.github_url.data,       # source code link
            tech_stack=form.tech_stack.data,       # comma-separated technologies
            sort_order=form.sort_order.data or 0,
            is_visible=form.is_visible.data,
        )
        db.session.add(item)
        db.session.commit()
        flash('Portfolio item added.', 'success')
        return redirect(url_for('dashboard.portfolio'))

    return render_template('dashboard/portfolio.html', site=site, form=form)


@dashboard_bp.route('/portfolio/<int:item_id>/edit', methods=['POST'])
@login_required
def edit_portfolio_item(item_id):
    site = _get_site_or_abort()

    # Fetch the item, confirming it belongs to this user's site
    item = PortfolioItem.query.filter_by(id=item_id, site_id=site.id).first_or_404()
    form = PortfolioItemForm()

    if form.validate_on_submit():
        # Update all fields with the submitted values
        item.title       = form.title.data
        item.description = form.description.data
        item.image_url   = form.image_url.data
        item.project_url = form.project_url.data
        item.github_url  = form.github_url.data
        item.tech_stack  = form.tech_stack.data
        item.sort_order  = form.sort_order.data or 0
        item.is_visible  = form.is_visible.data
        db.session.commit()
        flash('Portfolio item updated.', 'success')

    return redirect(url_for('dashboard.portfolio'))


@dashboard_bp.route('/portfolio/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_portfolio_item(item_id):
    site = _get_site_or_abort()
    item = PortfolioItem.query.filter_by(id=item_id, site_id=site.id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash('Portfolio item deleted.', 'info')
    return redirect(url_for('dashboard.portfolio'))
