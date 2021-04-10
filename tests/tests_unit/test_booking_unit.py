import pytest


@pytest.mark.parametrize('path', (
    '/book',
    '/book/competition1',
    '/book/competition1/fake_club',
    '/book/fake_competition1/club1',
))
def test_booking_url_does_not_exist(client, auth, path):
    auth.login()
    assert client.get(path).status_code == 404
    assert client.post(path).status_code == 404


def test_booking_authorized(client, auth, app):
    auth.login()
    assert client.get('/book/competition1/club1').status_code == 200
    response = client.post('/book/competition1/club1', data={'places': 1})
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/show_summary'


def test_booking_not_authorized(client, auth):
    # club1 is logged in and should not be allowed to book for club2
    auth.login()
    response = client.get('/book/competition1/club2')
    assert response.status_code == 403
    response = client.post('/book/competition1/club2', data={'places': 1})
    assert response.status_code == 403
