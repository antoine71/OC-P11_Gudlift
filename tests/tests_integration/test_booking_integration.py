import pytest

from flask import session

from gudlift.db import get_db


def test_show_summary_data(client, auth):
    auth.login()
    response = client.get('/show_summary')
    assert response.status_code == 200
    assert b'Summary' in response.data
    assert b'Logout' in response.data
    assert b'name1@club1.com' in response.data
    assert b'competition1' in response.data


def test_points_data(client):
    response = client.get('/points')
    assert b'club1: 10' in response.data
    assert b'club2: 1' in response.data
    assert b'club3: 15' in response.data


def test_booking_places_db_is_updated(client, auth, app):
    auth.login()
    client.post('/book/competition1/club1', data={'places': 1})
    client.post('/book/competition1/club1', data={'places': 2})
    with app.app_context():
        db = get_db()
        club = db.execute('SELECT * FROM clubs WHERE name = ?', ('club1',)
                          ).fetchone()
        competition = db.execute('SELECT * FROM competitions WHERE name = ?',
                                 ('competition1',)).fetchone()
        booking = db.execute('SELECT * FROM bookings WHERE club_id = ? AND '
                             'competition_id = ?',
                             (1, 1)).fetchone()
        assert int(club['points']) == 1
        assert int(competition['number_of_places']) == 8
        assert int(booking['places_booked']) == 3


def test_booking_places_confirmation_message(client, auth, app):
    auth.login()
    with client:
        response = client.post('/book/competition1/club1', data={'places': 1})
        assert response.headers['Location'] == 'http://localhost/show_summary'
        assert 'Great-booking completed! (1 place(s) for competition1)' in \
            dict(session['_flashes']).get('message')


@pytest.mark.parametrize(
    'path, places, expected_message',
    [
        ('/book/competition1/club1', 4, b'Warning: not enough points.'),
        ('/book/competition3/club1', 3, b'not enough places available'),
        ('/book/competition1/club1', -1, b'enter a number strictly positive.'),
        ('/book/competition4/club1', 6, b'too much places booked.'),
    ]
)
def test_booking_places_errors_messages(client, auth, path, places,
                                        expected_message):
    auth.login()
    response = client.post(path, data={'places': places})
    assert response.status_code == 200
    assert expected_message in response.data


def test_booking_past_competition_error_message(client, auth):
    auth.login()
    with client:
        response = client.get('/book/competition2/club1')
        assert response.status_code == 302
        assert response.headers['Location'] == 'http://localhost/show_summary'
        assert 'Something went wrong-please try again' in \
            dict(session['_flashes']).get('message')
    with client:
        response = client.post('/book/competition2/club1', data={'places': 1})
        assert response.status_code == 302
        assert response.headers['Location'] == 'http://localhost/show_summary'
        assert 'Something went wrong-please try again' in \
            dict(session['_flashes']).get('message')
