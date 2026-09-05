import pytest
from app import create_app
from app.models import db, User, Link


@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth_user(app):
    with app.app_context():
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def other_user(app):
    with app.app_context():
        user = User(username='otheruser', email='other@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user.id
