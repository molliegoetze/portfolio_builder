from flask import Blueprint, render_template, request
from models import db, Site, Profile
from forms import SERVICE_CATEGORIES

# Blueprint for the public directory / explorer page
search_bp = Blueprint('search', __name__)


@search_bp.route('/explore')
def index():
    # Read all filter values from the URL query string (e.g. /explore?q=designer&category=...)
    q            = request.args.get('q', '').strip()           # keyword search
    category     = request.args.get('category', '')            # service category dropdown
    location     = request.args.get('location', '').strip()    # location text filter
    remote_only  = request.args.get('remote') == '1'           # checkbox — only remote workers
    availability = request.args.get('availability', '')        # availability status filter
    sort         = request.args.get('sort', 'newest')          # sort order: newest or name

    # Base query — join Sites with their Profiles, only include published + searchable entries
    query = (
        db.session.query(Site, Profile)
        .join(Profile, Profile.site_id == Site.id)
        .filter(Site.is_published == True)       # site must be live
        .filter(Profile.is_searchable == True)   # profile owner must have opted in to the directory
    )

    # Keyword filter — searches across multiple profile fields (case-insensitive)
    if q:
        like = f'%{q}%'  # wrap in % wildcards for SQL LIKE/ILIKE
        query = query.filter(
            db.or_(
                Profile.display_name.ilike(like),
                Profile.headline.ilike(like),
                Profile.bio.ilike(like),
                Profile.occupation.ilike(like),
                Profile.skills.ilike(like),
                Profile.location.ilike(like),
            )
        )

    # Exact match on service category (e.g. "Photography", "Development")
    if category:
        query = query.filter(Profile.service_category == category)

    # Partial match on location text
    if location:
        query = query.filter(Profile.location.ilike(f'%{location}%'))

    # Only show profiles where the person works remotely
    if remote_only:
        query = query.filter(Profile.is_remote == True)

    # Filter by availability status (e.g. "available", "busy", "unavailable")
    if availability:
        query = query.filter(Profile.availability_status == availability)

    # Apply sort order — alphabetical by name, or newest site first (default)
    if sort == 'name':
        query = query.order_by(Profile.display_name.asc())
    else:
        query = query.order_by(Site.created_at.desc())

    # Execute the query — returns a list of (Site, Profile) tuples
    results = query.all()

    # Build the category list for the dropdown, skipping the empty placeholder entry
    categories = [c for c in SERVICE_CATEGORIES if c[0]]

    # Render the search results template, passing all filter state back so the form stays populated
    return render_template(
        'search/index.html',
        results=results,
        categories=categories,
        q=q,
        selected_category=category,
        selected_location=location,
        remote_only=remote_only,
        selected_availability=availability,
        sort=sort,
        total=len(results),   # total count displayed in the UI (e.g. "12 results")
    )
