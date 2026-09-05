import secrets
import string
import re
from datetime import datetime, timedelta, timezone
import validators

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, current_app
from flask_login import current_user
from app.models import db, Link, ClickLog

links_bp = Blueprint('links', __name__)


def parse_device_category(user_agent_str):
    if not user_agent_str:
        return 'Unknown'
    ua_lower = user_agent_str.lower()
    if any(bot_keyword in ua_lower for bot_keyword in ['bot', 'spider', 'crawler', 'slurp']):
        return 'Bot'
    if any(mobile_keyword in ua_lower for mobile_keyword in ['mobile', 'android', 'iphone', 'ipad', 'ipod', 'windows phone']):
        return 'Mobile'
    return 'Desktop'


def generate_code(length=6):
    characters = string.ascii_letters + string.digits
    for _ in range(20):
        code = ''.join(secrets.choice(characters) for _ in range(length))
        if not Link.query.filter_by(short_code=code).first():
            return code
    raise RuntimeError("Failed to generate a unique short code after multiple attempts.")


def validate_url(url):
    if not url:
        return False, "URL is required"
    url = url.strip()
    # Enforce safe schemes only
    if not (url.startswith('http://') or url.startswith('https://')):
        return False, "URL must start with http:// or https://"
    if not validators.url(url):
        return False, "Invalid URL format"
    return True, None


@links_bp.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    if request.method == 'POST':
        url = request.form.get('url', '').strip()
        custom = request.form.get('custom', '').strip()
        password = request.form.get('password', '').strip()
        expiry_days = request.form.get('expiry', 'Never')

        # Validate URL
        is_valid, err_msg = validate_url(url)
        if not is_valid:
            return render_template('index.html', error=err_msg)

        # Handle alias validation
        if custom:
            if not re.match(r'^[a-zA-Z0-9_-]+$', custom):
                return render_template('index.html', error="Invalid alias format. Use letters, numbers, underscores, or hyphens.")

            if len(custom) > 20:
                return render_template('index.html', error="Alias must be 20 characters or fewer.")

            # Reserved route names check
            reserved_routes = ['dashboard', 'login', 'register', 'logout', 'check-alias', 'api', 'delete', 'static']
            if custom.lower() in reserved_routes:
                return render_template('index.html', error="This alias is reserved. Please choose another.")

            existing = Link.query.filter_by(short_code=custom).first()
            if existing:
                return render_template('index.html', error="Custom alias already exists. Try another.")

            code = custom
        else:
            code = generate_code()

        # Handle expiry
        expiry_date = None
        if expiry_days != "Never":
            try:
                days = int(expiry_days)
                expiry_date = datetime.now(timezone.utc) + timedelta(days=days)
            except ValueError:
                expiry_date = None

        # Create link
        link = Link(
            original_url=url,
            short_code=code,
            expiry=expiry_date,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        if password:
            link.set_password(password)

        db.session.add(link)
        db.session.commit()

        short_url = request.host_url + code

    return render_template('index.html', short_url=short_url)


@links_bp.route('/check-alias')
def check_alias():
    alias = request.args.get('alias', '').strip()
    if not alias:
        return jsonify({'available': False})

    reserved = ['dashboard', 'login', 'register', 'logout', 'check-alias', 'api', 'delete', 'static']
    if alias.lower() in reserved:
        return jsonify({'available': False})

    existing = Link.query.filter_by(short_code=alias).first()
    return jsonify({'available': existing is None})


@links_bp.route('/<code>', methods=['GET', 'POST'])
def redirect_link(code):
    link = Link.query.filter_by(short_code=code).first()

    if not link:
        return render_template('errors/404.html'), 404

    if link.is_expired():
        return render_template('expired.html', link=link), 410

    # Handle Password Protection
    if link.password:
        if request.method == 'POST':
            input_pwd = request.form.get('password', '')
            if link.check_password(input_pwd):
                _record_click(link)
                return render_template('preview.html', link=link)
            else:
                return render_template('password.html', link=link, error="Wrong password. Try again.")
        return render_template('password.html', link=link)

    # Direct click (no password)
    _record_click(link)
    return render_template('preview.html', link=link)


def _record_click(link):
    link.clicks += 1
    user_agent = request.headers.get('User-Agent', '')
    referrer = request.referrer or request.headers.get('Referer')
    if referrer and len(referrer) > 500:
        referrer = referrer[:500]

    device = parse_device_category(user_agent)
    click_log = ClickLog(
        link_id=link.id,
        referrer=referrer,
        user_agent_category=device
    )
    db.session.add(click_log)
    db.session.commit()
