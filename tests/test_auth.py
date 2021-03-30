import pytest

from flask import session


def test_login(client, auth):
    assert client.get('/').status_code == 200
    response = auth.login()
    assert response.headers['Location'] == 'http://localhost/show_summary'

    with client:
        client.get('/show_summary')
        assert session['user_id'] == 'name1@club1.com'


@pytest.mark.parametrize(('email', 'message'), (
    ('incorrect@email.com', b'is not registered'),
    ('', b'is required'),
))
def test_login_validate_input(auth, email, message):
    response = auth.login(email)
    assert message in response.data


def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session
