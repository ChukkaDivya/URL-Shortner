def test_registration_success(client):
    response = client.post('/register', data={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'securepassword'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Welcome to SwiftLink' in response.data or b'Dashboard' in response.data


def test_registration_duplicate_username(client, auth_user):
    response = client.post('/register', data={
        'username': 'testuser',
        'email': 'different@example.com',
        'password': 'securepassword'
    })

    assert response.status_code == 200
    assert b'Username is already taken' in response.data


def test_registration_duplicate_email(client, auth_user):
    response = client.post('/register', data={
        'username': 'uniqueusername',
        'email': 'test@example.com',
        'password': 'securepassword'
    })

    assert response.status_code == 200
    assert b'Email is already registered' in response.data


def test_login_success(client, auth_user):
    response = client.post('/login', data={
        'identity': 'testuser',
        'password': 'password123'
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b'Welcome back, testuser' in response.data


def test_login_failure(client, auth_user):
    response = client.post('/login', data={
        'identity': 'testuser',
        'password': 'wrongpassword'
    })

    assert response.status_code == 200
    assert b'Invalid username/email or password' in response.data


def test_logout(client, auth_user):
    # Log in first
    client.post('/login', data={
        'identity': 'testuser',
        'password': 'password123'
    })

    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'You have been logged out' in response.data
