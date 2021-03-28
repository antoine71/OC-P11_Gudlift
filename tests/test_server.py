from gudlift.server import app

client = app.test_client()


def test_index():
    email_in_list = 'admin@irontemple.com'
    email_not_in_list = 'example@example.com'
    no_email = ''

    response = client.post("/", data={'email': email_in_list})
    assert response.status_code == 302

    response = client.post("/", data={'email': email_not_in_list})
    assert "The email {0} is not registered.".format(email_not_in_list)\
        in str(response.data)

    response = client.post("/", data={'email': no_email})
    assert "Email is required." in str(response.data)
