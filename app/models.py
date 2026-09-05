from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    links = db.relationship('Link', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Link(db.Model):
    __tablename__ = 'link'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    original_url = db.Column(db.String(2048), nullable=False)
    short_code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    clicks = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expiry = db.Column(db.DateTime, nullable=True)
    password = db.Column(db.String(256), nullable=True)  # Securely hashed link password

    click_logs = db.relationship('ClickLog', backref='link', lazy=True, cascade="all, delete-orphan")

    def set_password(self, raw_password):
        if raw_password and raw_password.strip():
            self.password = generate_password_hash(raw_password.strip())
        else:
            self.password = None

    def check_password(self, raw_password):
        if not self.password:
            return True
        if not raw_password:
            return False
        # Support backward compatibility with legacy plain text passwords if any exist
        if self.password == raw_password:
            return True
        return check_password_hash(self.password, raw_password)

    def is_expired(self):
        if self.expiry is None:
            return False
        # Normalize expiry comparison
        now = datetime.now(timezone.utc)
        if self.expiry.tzinfo is None:
            return datetime.now() > self.expiry
        return now > self.expiry

    def __repr__(self):
        return f'<Link {self.short_code} -> {self.original_url}>'


class ClickLog(db.Model):
    __tablename__ = 'click_log'

    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('link.id', ondelete='CASCADE'), nullable=False)
    clicked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    referrer = db.Column(db.String(500), nullable=True)
    user_agent_category = db.Column(db.String(50), nullable=True)

    def __repr__(self):
        return f'<ClickLog link_id={self.link_id} at={self.clicked_at}>'
