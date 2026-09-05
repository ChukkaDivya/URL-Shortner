from datetime import datetime, timedelta, timezone
from app.models import db, Link


def test_shorten_valid_url(client):
    response = client.post('/', data={
        'url': 'https://example.com'
    })
    assert response.status_code == 200
    assert b'Your shortened link' in response.data


def test_shorten_invalid_url_format(client):
    response = client.post('/', data={
        'url': 'invalid-url-string'
    })
    assert response.status_code == 200
    assert b'Invalid URL format' in response.data or b'must start with http' in response.data


def test_shorten_invalid_url_scheme(client):
    response = client.post('/', data={
        'url': 'javascript:alert("hacked")'
    })
    assert response.status_code == 200
    assert b'must start with http:// or https://' in response.data


def test_custom_alias_success(client):
    response = client.post('/', data={
        'url': 'https://python.org',
        'custom': 'myalias'
    })
    assert response.status_code == 200
    assert b'/myalias' in response.data


def test_duplicate_custom_alias(client):
    client.post('/', data={
        'url': 'https://python.org',
        'custom': 'myalias'
    })

    response = client.post('/', data={
        'url': 'https://flask.palletsprojects.com',
        'custom': 'myalias'
    })
    assert response.status_code == 200
    assert b'Custom alias already exists' in response.data


def test_alias_availability_api(client):
    res1 = client.get('/check-alias?alias=freealias')
    assert res1.json['available'] is True

    client.post('/', data={'url': 'https://google.com', 'custom': 'freealias'})

    res2 = client.get('/check-alias?alias=freealias')
    assert res2.json['available'] is False


def test_password_protected_link_access(client):
    # Shorten with password
    client.post('/', data={
        'url': 'https://secret.com',
        'custom': 'secretlink',
        'password': 'linkpassword'
    })

    # Access without submitting password -> prompt page
    res_get = client.get('/secretlink')
    assert res_get.status_code == 200
    assert b'Password Required' in res_get.data

    # Submit wrong password
    res_wrong = client.post('/secretlink', data={'password': 'wrong'})
    assert res_wrong.status_code == 200
    assert b'Wrong password' in res_wrong.data

    # Submit correct password -> renders preview page
    res_correct = client.post('/secretlink', data={'password': 'linkpassword'})
    assert res_correct.status_code == 200
    assert b'You are about to visit' in res_correct.data
    assert b'https://secret.com' in res_correct.data


def test_expired_link_access(app, client):
    with app.app_context():
        past_expiry = datetime.now(timezone.utc) - timedelta(days=1)
        link = Link(
            original_url='https://expired.com',
            short_code='oldlink',
            expiry=past_expiry
        )
        db.session.add(link)
        db.session.commit()

    response = client.get('/oldlink')
    assert response.status_code == 410
    assert b'Link Expired' in response.data


def test_link_authorization_deletion(app, client, auth_user, other_user):
    # Create link for auth_user
    with app.app_context():
        link = Link(original_url='https://user1.com', short_code='u1link', user_id=auth_user)
        db.session.add(link)
        db.session.commit()

    # Log in as other_user
    client.post('/login', data={'identity': 'otheruser', 'password': 'password123'})

    # Try to delete auth_user's link -> should return 403 Forbidden
    res_delete = client.post('/delete/u1link')
    assert res_delete.status_code == 403
