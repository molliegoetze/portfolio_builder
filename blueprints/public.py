from flask import Blueprint, render_template, abort
from models import Site

# Blueprint for public-facing pages — no login required
public_bp = Blueprint('public', __name__)


@public_bp.route('/u/<subdomain>')
def profile(subdomain):
    # Look up the site by its subdomain (e.g. /u/jane); return 404 if not found
    site = Site.query.filter_by(subdomain=subdomain).first_or_404()

    # If the owner hasn't published their page yet, treat it as not found
    if not site.is_published:
        abort(404)

    # Filter out items the owner has hidden — only show what's marked visible
    visible_links     = [l for l in site.links          if l.is_visible]
    visible_images    = [i for i in site.images         if i.is_visible]
    visible_portfolio = [p for p in site.portfolio_items if p.is_visible]

    # Render the public profile template with all the data the template needs
    return render_template(
        'public/profile.html',
        site=site,
        profile=site.profile,
        links=visible_links,
        images=visible_images,
        portfolio=visible_portfolio,
    )
