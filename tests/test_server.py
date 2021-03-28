from gudlift.server import app, clubs

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
    club = 'Iron Temple'
    competition = 'Spring Festival'
    club_ = [club_ for club_ in clubs if club_['name'] == club][0]
    current_points = int(club_['points'])

    required_places = 3
    response = client.post("/purchasePlaces", data={
        'club': club,
        'competition': competition,
        'places': required_places})
    assert "Great-booking complete!" in str(response.data)
    current_points -= required_places
    assert int(club_['points']) == current_points

    required_places = 6
    response = client.post("/purchasePlaces", data={
        'club': club,
        'competition': competition,
        'places': required_places})
    assert 'Warning: you have only' in str(response.data)
    assert int(club_['points']) == current_points

    required_places = 1
    response = client.post("/purchasePlaces", data={
        'club': club,
        'competition': competition,
        'places': required_places})
    assert "Great-booking complete!" in str(response.data)
    current_points -= required_places
    assert int(club_['points']) == current_points
