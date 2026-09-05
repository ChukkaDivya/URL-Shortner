import re
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, jsonify
from flask_login import current_user
from app.models import db, Link
from app.routes.links import validate_url, generate_code

api_bp = Blueprint('api', __name__)


@api_bp.route('/links', methods=['POST'])
def api_create_link():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Invalid JSON body'}), 400

    url = data.get('url', '').strip()
    custom_alias = data.get('custom_alias', '').strip()
    password = data.get('password', '').strip()
    expiry_days = data.get('expiry_days')

    # Validate URL
    is_valid, err_msg = validate_url(url)
    if not is_valid:
        return jsonify({'error': err_msg}), 400

    # Custom alias logic
    if custom_alias:
        if not re.match(r'^[a-zA-Z0-9_-]+$', custom_alias):
            return jsonify({'error': 'Invalid custom alias format'}), 400
        if len(custom_alias) > 20:
            return jsonify({'error': 'Custom alias exceeds 20 characters'}), 400

        reserved = ['dashboard', 'login', 'register', 'logout', 'check-alias', 'api', 'delete', 'static']
        if custom_alias.lower() in reserved:
            return jsonify({'error': 'Custom alias is reserved'}), 409

        existing = Link.query.filter_by(short_code=custom_alias).first()
        if existing:
            return jsonify({'error': 'Custom alias already exists'}), 409

        code = custom_alias
    else:
        try:
            code = generate_code()
        except RuntimeError:
            return jsonify({'error': 'Failed to generate unique short code'}), 500

    # Expiry
    expires_at = None
    if expiry_days:
        try:
            days = int(expiry_days)
            expires_at = datetime.now(timezone.utc) + timedelta(days=days)
        except ValueError:
            return jsonify({'error': 'expiry_days must be an integer'}), 400

    user_id = current_user.id if current_user.is_authenticated else None
    link = Link(
        original_url=url,
        short_code=code,
        expiry=expires_at,
        user_id=user_id
    )
    if password:
        link.set_password(password)

    db.session.add(link)
    db.session.commit()

    return jsonify({
        'short_url': request.host_url + code,
        'short_code': code,
        'original_url': url,
        'created_at': link.created.isoformat() if link.created else None,
        'expires_at': link.expiry.isoformat() if link.expiry else None,
        'is_protected': bool(link.password)
    }), 201


@api_bp.route('/links/<short_code>', methods=['GET'])
def api_get_link(short_code):
    link = Link.query.filter_by(short_code=short_code).first()
    if not link:
        return jsonify({'error': 'Link not found'}), 404

    return jsonify({
        'short_code': link.short_code,
        'original_url': link.original_url,
        'clicks': link.clicks,
        'created_at': link.created.isoformat() if link.created else None,
        'expires_at': link.expiry.isoformat() if link.expiry else None,
        'is_protected': bool(link.password),
        'is_expired': link.is_expired()
    }), 200
