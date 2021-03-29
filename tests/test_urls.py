import pytest
from urllib.parse import quote

from flask import session

from gudlift.server import app

client = app.test_client()


@pytest.mark.parametrize("path", (quote("/show_summary/wrong_url"),
                                  quote("/book/wrong_url"),
                                  quote("/book/wrong_url/wrong_url"),
                                  quote("/wrong_url"),
                                  quote("/points/wrong_url"),
                                  ))
def test_login_required_get(path):
    with client.session_transaction() as sess:
        sess['user_id'] = "john@simplylift.co"
        response = client.get(path)
    assert response.status_code == 404
