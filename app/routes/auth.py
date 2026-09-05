import re
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User

auth_bp = Blueprint('auth', __name__)


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        # Input validation
        if not username or not email or not password:
            flash('All fields are required.', 'error')
            return render_template('register.html', username=username, email=email)

        if len(username) < 3 or len(username) > 30 or not re.match(r'^[a-zA-Z0-9_-]+$', username):
            flash('Username must be 3-30 characters long and contain only letters, numbers, underscores, or hyphens.', 'error')
            return render_template('register.html', username=username, email=email)

        if not is_valid_email(email):
            flash('Please enter a valid email address.', 'error')
            return render_template('register.html', username=username, email=email)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'error')
            return render_template('register.html', username=username, email=email)

        # Check existing user
        if User.query.filter(db.func.lower(User.username) == username.lower()).first():
            flash('Username is already taken.', 'error')
            return render_template('register.html', username=username, email=email)

        if User.query.filter(db.func.lower(User.email) == email).first():
            flash('Email is already registered.', 'error')
            return render_template('register.html', username=username, email=email)

        # Create new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash('Account created successfully! Welcome to SwiftLink.', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.dashboard'))

    if request.method == 'POST':
        identity = request.form.get('identity', '').strip()  # Username or Email
        password = request.form.get('password', '')

        if not identity or not password:
            flash('Please enter both username/email and password.', 'error')
            return render_template('login.html', identity=identity)

        # Find user by username or email
        user = User.query.filter(
            (db.func.lower(User.username) == identity.lower()) | 
            (db.func.lower(User.email) == identity.lower())
        ).first()

        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('dashboard.dashboard'))

        flash('Invalid username/email or password.', 'error')
        return render_template('login.html', identity=identity)

    return render_template('login.html')


@auth_bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('links.index'))
