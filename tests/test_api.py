def test_api_create_link_success(client):
    res = client.post('/api/v1/links', json={
        'url': 'https://example.com',
        'custom_alias': 'apialias',
        'expiry_days': 7
    })
    assert res.status_code == 201
    data = res.json
    assert data['short_code'] == 'apialias'
    assert 'short_url' in data
    assert data['original_url'] == 'https://example.com'


def test_api_create_link_invalid_url(client):
    res = client.post('/api/v1/links', json={
        'url': 'javascript:alert(1)'
    })
    assert res.status_code == 400
    assert 'error' in res.json


def test_api_create_link_duplicate_alias(client):
    client.post('/api/v1/links', json={'url': 'https://google.com', 'custom_alias': 'dupe'})
    res = client.post('/api/v1/links', json={'url': 'https://bing.com', 'custom_alias': 'dupe'})

    assert res.status_code == 409
    assert res.json['error'] == 'Custom alias already exists'


def test_api_get_link(client):
    client.post('/api/v1/links', json={'url': 'https://testapi.com', 'custom_alias': 'getlink'})

    res = client.get('/api/v1/links/getlink')
    assert res.status_code == 200
    data = res.json
    assert data['short_code'] == 'getlink'
    assert data['original_url'] == 'https://testapi.com'
    assert data['clicks'] == 0


def test_api_get_nonexistent_link(client):
    res = client.get('/api/v1/links/nonexistent')
    assert res.status_code == 404
