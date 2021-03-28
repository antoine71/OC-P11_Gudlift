from gudlift.server import app

client = app.test_client()


def test_show_summary():
    email_in_list = 'admin@irontemple.com'
    email_not_in_list = 'example@example.com'

    response = client.post("/showSummary", data={'email': email_in_list})
    assert response.status_code == 200
    assert email_in_list in str(response.data)

    response = client.post("/showSummary", data={'email': email_not_in_list})
    assert response.status_code == 302
