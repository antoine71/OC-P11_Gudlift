from urllib.parse import quote
from datetime import datetime

import gudlift

client = gudlift.server.app.test_client()


def mock_load_clubs():
    return [
            {
                "name": "Simply Lift",
                "email": "john@simplylift.co",
                "points": "1"
            },
            {
                "name": "Iron Temple",
                "email": "admin@irontemple.com",
                "points": "4"
            },
            {
                "name": "She Lifts",
                "email": "kate@shelifts.co.uk",
                "points": "12"
            }
        ]


def mock_load_competitions():
    return [
            {
                "name": "Spring Festival",
                "date": datetime.fromisoformat("2021-05-27 10:00:00"),
                "number_of_places": "25"
            },
            {
                "name": "Fall Classic",
                "date": datetime.fromisoformat("2020-10-22 13:30:00"),
                "number_of_places": "13"
            }
        ]


def test_index():
    email_in_list = 'admin@irontemple.com'
    email_not_in_list = 'example@example.com'
    no_email = ''

    response = client.post("/", data={'email': email_in_list})
    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost/show_summary'

    response = client.post("/", data={'email': email_not_in_list})
    assert "The email {0} is not registered.".format(email_not_in_list)\
        in str(response.data)

    response = client.post("/", data={'email': no_email})
    assert "Email is required." in str(response.data)


def test_purchase_places(monkeypatch):
    monkeypatch.setattr('gudlift.server.loadClubs', mock_load_clubs)
    monkeypatch.setattr('gudlift.server.loadCompetitions', mock_load_competitions)
    club = 'Simply Lift'
    competition = 'Spring Festival'
    club_ = [club_ for club_ in gudlift.server.clubs if club_['name'] == club][0]
    print(club_)
    print(gudlift.server.clubs)
    print(gudlift.server.loadClubs())
    competition_ = [competition_ for competition_ in gudlift.server.competitions
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
    assert response.headers['location'] == 'http://localhost/show_summary'
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
    assert response.headers['location'] == 'http://localhost/show_summary'
    current_points -= required_places
    current_places -= required_places
    assert int(club_['points']) == current_points
    assert int(competition_['number_of_places']) == current_places

    required_places = -1
    response = client.post(quote("/book/" + competition + "/" + club), data={
        'places': required_places})
    assert 'Please enter a number strictly positive' in str(response.data)
    assert int(club_['points']) == current_points
    assert int(competition_['number_of_places']) == current_places


def test_show_summary():
    response = client.get(quote("/book/Spring Festival/Simply Lift"))
    assert response.status_code == 200

    response = client.get(quote("/book/Fall Classic/Simply Lift"))
    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost/show_summary'


def points():
    response = client.get("/points")
    assert response.status_code == 200


def test_logout():
    response = client.get(quote("/logout"))
    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost/'
    response = client.get(quote("/show_summary"))
    assert response.status_code == 302
    assert response.headers['location'] == 'http://localhost/'
