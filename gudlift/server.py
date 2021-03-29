import json
from datetime import datetime
from urllib.parse import unquote

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import flash
from flask import session
from flask import url_for
from flask import abort
from .auth import login_required


def loadClubs():
    with open('gudlift/clubs.json') as c:
        listOfClubs = json.load(c)['clubs']
        return listOfClubs


def loadCompetitions():
    with open('gudlift/competitions.json') as comps:
        list_of_competitions = json.load(comps)['competitions']
        for competition in list_of_competitions:
            competition['date'] = datetime.fromisoformat(competition['date'])
        return list_of_competitions


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
        elif not [club for club in clubs if club['email'] ==
                  request.form['email']]:
            error = "The email {0} is not registered.".format(email)

        if error is None:
            session.clear()
            session["user_id"] = email
            return redirect(url_for('show_summary'))

        flash(error)

    return render_template('index.html')


@app.route('/show_summary')
@login_required
def show_summary():
    club = [club for club in clubs if club['email'] == session["user_id"]]
    upcoming_competitions = [competition for competition in competitions
                             if competition['date'] >= datetime.now()]
    past_competitions = [competition for competition in competitions
                         if competition['date'] < datetime.now()]
    if club:
        return render_template('welcome.html', club=club[0],
                               competitions=upcoming_competitions,
                               past_competitions=past_competitions)
    else:
        return redirect(url_for('index'))


@app.route('/book/<competition>/<club>', methods=['GET', 'POST'])
@login_required
def book(competition, club):
    competition = unquote(competition)
    club = unquote(club)
    try:
        club = [c for c in clubs if c['name'] == club][0]
        competition = [c for c in competitions if c['name'] == competition][0]
    except IndexError:
        abort(404)
    if club and competition and \
            competition['date'] >= datetime.now():

        if request.method == 'POST':
            if not request.form['places'].isnumeric():
                placesRequired = 0
            else:
                placesRequired = int(request.form['places'])
            points = int(club['points'])
            max_number_of_places = 12
            try:
                already_booked_places = \
                    int(club['competitions'][competition['name']])
            except KeyError:
                already_booked_places = 0
            error = []

            if placesRequired <= 0:
                error.append('Please enter a number strictly positive')

            if placesRequired > points:
                error.append('Warning: not enough points. You have only {0} \
                             available points, you can not book more than {0} \
                             places.'.format(points))

            if placesRequired > max_number_of_places - already_booked_places:
                error.append('Warning: too much places booked. You can not \
                            book more than{0} places per competition (places \
                            previously booked: {1}).'.format(
                                max_number_of_places, already_booked_places))

            if not error:
                competition['number_of_places'] = \
                    int(competition['number_of_places']) - placesRequired
                club['points'] = int(club['points']) - placesRequired
                try:
                    club['competitions']
                except KeyError:
                    club['competitions'] = {}
                club['competitions'][competition['name']] = \
                    placesRequired + already_booked_places
                flash('Great-booking complete!')
                return redirect(url_for('show_summary'))

            for message in error:
                flash(message)

        return render_template('booking.html', club=club,
                               competition=competition)

    else:
        flash("Something went wrong-please try again")
        return redirect(url_for('show_summary'))


@app.route('/points')
def points():
    return render_template('points.html', clubs=clubs)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))
