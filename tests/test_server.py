from urllib.parse import quote

from gudlift.server import app, clubs, competitions

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


def test_purchase_places():
    club = 'Simply Lift'
    competition = 'Spring Festival'
    club_ = [club_ for club_ in clubs if club_['name'] == club][0]
    competition_ = [competition_ for competition_ in competitions
                    if competition_['name'] == competition][0]
    current_points = int(club_['points'])
    current_places = int(competition_['number_of_places'])

    required_places = 13
    response = client.post(quote("/book/Spring Festival/Simply Lift"), data={
        'places': required_places})
    assert "Warning: too much places booked." in str(response.data)
    assert int(club_['points']) == current_points
    assert int(competition_['number_of_places']) == current_places

    required_places = 3
    response = client.post(quote("/book/" + competition + "/" + club), data={
        'places': required_places})
    assert response.status_code == 302
    current_points -= required_places
    current_places -= required_places
    assert int(club_['points']) == current_points
    assert int(competition_['number_of_places']) == current_places

    required_places = 11
    response = client.post(quote("/book/" + competition + "/" + club), data={
        'places': required_places})
    assert 'Warning: not enough points.' in str(response.data)
    assert int(club_['points']) == current_points
    assert int(competition_['number_of_places']) == current_places

    required_places = 1
    response = client.post(quote("/book/" + competition + "/" + club), data={
        'places': required_places})
    assert response.status_code == 302
    current_points -= required_places
    current_places -= required_places
    assert int(club_['points']) == current_points
    assert int(competition_['number_of_places']) == current_places


def test_show_summary():
    response = client.get(quote("/book/Spring Festival/Simply Lift"))
    assert response.status_code == 200

    response = client.get(quote("/book/Fall Classic/Simply Lift"))
    assert response.status_code == 302


def points():
    response = client.get("/points")
    assert response.status_code == 200
