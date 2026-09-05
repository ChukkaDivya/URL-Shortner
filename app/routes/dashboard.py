from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.models import db, Link

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard():
    page = request.args.get('page', 1, type=int)
    per_page = 15  # Pagination

    # Query only links belonging to the logged-in user
    query = Link.query.filter_by(user_id=current_user.id).order_by(Link.created.desc())

    # Aggregate metrics for the user's links
    all_user_links = Link.query.filter_by(user_id=current_user.id).all()
    total_links = len(all_user_links)
    total_clicks = sum(link.clicks for link in all_user_links)

    active_links = 0
    protected_links = 0
    expired_links = 0

    now = datetime.now(timezone.utc)
    for link in all_user_links:
        if link.is_expired():
            link.status = "Expired"
            expired_links += 1
        elif link.password:
            link.status = "Protected"
            protected_links += 1
        else:
            link.status = "Active"
            active_links += 1

    # Paginate links for display
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    page_links = pagination.items

    # Annotate status on paginated items
    for link in page_links:
        if link.is_expired():
            link.status = "Expired"
        elif link.password:
            link.status = "Protected"
        else:
            link.status = "Active"

    return render_template(
        'dashboard.html',
        links=page_links,
        pagination=pagination,
        total_links=total_links,
        total_clicks=total_clicks,
        active_links=active_links,
        protected_links=protected_links,
        expired_links=expired_links
    )


@dashboard_bp.route('/delete/<code>', methods=['POST'])
@login_required
def delete(code):
    link = Link.query.filter_by(short_code=code).first()

    if not link:
        flash('Link not found.', 'error')
        return redirect(url_for('dashboard.dashboard'))

    # Authorization Check: User can only delete their own links
    if link.user_id != current_user.id:
        abort(403)

    db.session.delete(link)
    db.session.commit()
    flash(f'Link /{code} deleted successfully.', 'success')

    return redirect(url_for('dashboard.dashboard'))
