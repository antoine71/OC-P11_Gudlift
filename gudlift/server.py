import json
from flask import Flask,render_template,request,redirect,flash,url_for, session


def loadClubs():
    with open('gudlift/clubs.json') as c:
         listOfClubs = json.load(c)['clubs']
         return listOfClubs


def loadCompetitions():
    with open('gudlift/competitions.json') as comps:
         listOfCompetitions = json.load(comps)['competitions']
         return listOfCompetitions


app = Flask(__name__)
app.secret_key = 'something_special'

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        email = request.form["email"]
        error = None
        if not email:
            error = "Email is required."
        elif not [club for club in clubs if club['email'] == request.form['email']]:
            error = "The email {0} is not registered.".format(email)

        if error is None:
            session.clear()
            session["user_id"] = email
            return redirect(url_for('showSummary'))

        flash(error)

    return render_template('index.html')

@app.route('/showSummary')
def showSummary():
    club = [club for club in clubs if club['email'] == session["user_id"]]
    if club:
        return render_template('welcome.html', club=club[0],
                               competitions=competitions)
    else:
        return redirect(url_for('index'))


@app.route('/book/<competition>/<club>')
def book(competition,club):
    foundClub = [c for c in clubs if c['name'] == club][0]
    foundCompetition = [c for c in competitions if c['name'] == competition][0]
    if foundClub and foundCompetition:
        return render_template('booking.html',club=foundClub,competition=foundCompetition)
    else:
        flash("Something went wrong-please try again")
        return render_template('welcome.html', club=club, competitions=competitions)


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition = [c for c in competitions if c['name'] == request.form['competition']][0]
    club = [c for c in clubs if c['name'] == request.form['club']][0]
    placesRequired = int(request.form['places'])
    points = int(club['points'])
    max_number_of_places = 12
    try:
        already_booked_places = int(club['competitions'][competition['name']])
    except KeyError:
        already_booked_places = 0
    error = []

    if placesRequired > points:
        error.append('Warning: not enough points. You have only {0} available \
            points, you can not book more than {0} places.'.format(points))

    if placesRequired > max_number_of_places - already_booked_places:
        error.append('Warning: too much places booked. You can not book more \
                     than{0} places per competition (places previously \
                     booked: {1}).'
                     .format(max_number_of_places, already_booked_places))

    if not error:
        competition['numberOfPlaces'] = \
            int(competition['numberOfPlaces']) - placesRequired
        club['points'] = int(club['points']) - placesRequired
        try:
            club['competitions']
        except KeyError:
            club['competitions'] = {}
        club['competitions'][competition['name']] = placesRequired + already_booked_places
        flash('Great-booking complete!')
        return render_template('welcome.html', club=club, competitions=competitions)
    
    for message in error:
        flash(message)

    return render_template('booking.html', club=club, competition=competition)


# TODO: Add route for points display


@app.route('/logout')
def logout():
    return redirect(url_for('index'))
