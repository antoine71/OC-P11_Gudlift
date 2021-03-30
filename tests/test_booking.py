import pytest

from gudlift.db import get_db


def test_index(client, auth):
    response = client.get('/show_summary')
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/'

    auth.login()
    response = client.get('/show_summary')
    assert b'Summary' in response.data
    assert b'Logout' in response.data
    assert b'name1@club1.com' in response.data
    assert b'competition1' in response.data


@pytest.mark.parametrize('path', (
    '/book/competition1/club1',
    '/book/competition2/club1',
))
def test_login_required(client, path):
    response = client.get(path)
    assert response.headers['Location'] == 'http://localhost/'
    response = client.post(path)
    assert response.headers['Location'] == 'http://localhost/'


@pytest.mark.parametrize('path', (
    '/book',
    '/book/competition1',
    '/book/competition1/fake_club',
    '/book/fake_competition1/club1',
))
def test_exists_required(client, auth, path):
    auth.login()
    assert client.get(path).status_code == 404
    assert client.post(path).status_code == 404


def test_book_places(client, auth, app):
    auth.login()
    assert client.get('/book/competition1/club1').status_code == 200
    response = client.post('/book/competition1/club1', data={'places': 1})
    assert response.status_code == 302
    response = client.post('/book/competition1/club1', data={'places': 2})
    assert response.status_code == 302

    with app.app_context():
        db = get_db()
        club = db.execute('SELECT * FROM clubs WHERE name = ?', ('club1',)
                          ).fetchone()
        competition = db.execute('SELECT * FROM competitions WHERE name = ?',
                                 ('competition1',)).fetchone()
        booking = db.execute('SELECT * FROM bookings WHERE club_id = ? AND '
                             'competition_id = ?',
                             (1, 1)).fetchone()
        assert int(club['points']) == 7
        assert int(competition['number_of_places']) == 8
        assert int(booking['places_booked']) == 3


@pytest.mark.parametrize(
    'path, places, expected_message',
    [
        ('/book/competition1/club1', 11, b'Warning: not enough points.'),
        ('/book/competition3/club1', 3, b'not enough places available'),
        ('/book/competition1/club1', -1, b'enter a number strictly positive.'),
        ('/book/competition4/club1', 6, b'too much places booked.'),
    ]
)
def test_book_places_errors(client, auth, path, places, expected_message):
    auth.login()
    response = client.post(path, data={'places': places})
    assert response.status_code == 200
    assert expected_message in response.data


def test_book_places_past_competition(client, auth):
    auth.login()
    response = client.get('/book/competition2/club1')
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/show_summary'
    response = client.post('/book/competition2/club1', data={'places': 1})
    assert response.status_code == 302
    assert response.headers['Location'] == 'http://localhost/show_summary'


def test_points(client):
    response = client.get('/points')
    assert response.status_code == 200
    assert b'club1: 10' in response.data
    assert b'club2: 1' in response.data
    assert b'club3: 15' in response.data
