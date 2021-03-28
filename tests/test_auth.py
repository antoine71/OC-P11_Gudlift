import pytest

from gudlift.server import app

client = app.test_client()


@pytest.mark.parametrize("path", ("/showSummary",
                                  "/book/Spring Festival/Simply Lift",
                                  ))
def test_login_required_get(path):
    response = client.get(path)
    assert response.status_code == 302


@pytest.mark.parametrize("path", ("/purchasePlaces",))
def test_login_required_post(path):
    response = client.post(path)
    assert response.status_code == 302


@pytest.mark.parametrize("path", ("/",
                                  "/points",
                                  ))
def test_login_not_required(path):
    response = client.get(path)
    assert response.status_code == 200
