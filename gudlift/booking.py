from datetime import datetime
from urllib.parse import unquote

from flask import render_template
from flask import request
from flask import redirect
from flask import flash
from flask import session
from flask import url_for
from flask import abort
from flask import Blueprint
from flask import g

from gudlift.auth import login_required
from gudlift.db import get_db


bp = Blueprint('booking', __name__, url_prefix='/')


@bp.route('/show_summary')
@login_required
def show_summary():
    db = get_db()
    clubs = db.execute(
        'SELECT * FROM clubs'
    ).fetchall()
    competitions = db.execute(
        'SELECT * FROM competitions'
    ).fetchall()
    club = [club for club in clubs if club['email'] == session['user_id']]
    upcoming_competitions = [competition for competition in competitions
                             if competition['date'] >= datetime.now()]
    past_competitions = [competition for competition in competitions
                         if competition['date'] < datetime.now()]

    return render_template('booking/welcome.html', club=club[0],
                           competitions=upcoming_competitions,
                           past_competitions=past_competitions)


@bp.route('/book/<competition>/<club>', methods=['GET', 'POST'])
@login_required
def book(competition, club):
    db = get_db()
    clubs = db.execute(
        'SELECT * FROM clubs'
    ).fetchall()
    competitions = db.execute(
        'SELECT * FROM competitions'
    ).fetchall()
    competition_name = unquote(competition)
    club_name = unquote(club)
    try:
        club = [c for c in clubs if c['name'] == club_name][0]
        competition = [c for c in competitions if c['name'] == competition_name][0]
    except IndexError:
        abort(404)
    if club['email'] != g.user:
        abort(403)
    if club and competition and competition['date'] >= datetime.now():
        if request.method == 'POST':
            if not request.form['places'].isnumeric():
                places_required = 0
            else:
                places_required = int(request.form['places'])
            points = int(club['points'])
            max_number_of_places = 12
            cost = 3 * places_required
            booking = db.execute(
                    'SELECT * FROM bookings WHERE club_id = ? '
                    'AND competition_id = ?',
                    (int(club['id']), int(competition['id']))).fetchone()
            if booking:
                already_booked_places = int(booking['places_booked'])
            else:
                already_booked_places = 0

            error = []

            if places_required <= 0:
                error.append('Please enter a number strictly positive.')

            if places_required > int(competition['number_of_places']):
                error.append('Warning: not enough places available for this '
                             'competition.')

            if cost > points:
                error.append('Warning: not enough points. You have only {0} '
                             'available points, you can not book more than '
                             '{0} places.'.format(points))

            if places_required > max_number_of_places - already_booked_places:
                error.append('Warning: too much places booked. You can not '
                             'book more than {0} places per competition '
                             '(places previously booked: {1}).'.format(
                                max_number_of_places, already_booked_places))

            if not error:
                remaining_number_of_places = \
                    int(competition['number_of_places']) - places_required
                remaining_points = int(club['points']) - cost
                places_booked = places_required + already_booked_places

                db.execute(
                    'UPDATE clubs SET points = ? WHERE id = ?',
                    (remaining_points, int(club['id']))
                )
                db.execute(
                    'UPDATE competitions SET number_of_places = ? '
                    'WHERE id = ?',
                    (remaining_number_of_places, int(competition['id']))
                )
                if booking:
                    db.execute(
                        'UPDATE bookings SET places_booked = ? WHERE '
                        'club_id = ? AND  competition_id = ?',
                        (places_booked, int(club['id']),
                         int(competition['id']))
                        )
                else:
                    db.execute(
                        'INSERT INTO bookings '
                        '(club_id, competition_id, places_booked) '
                        'VALUES (?, ?, ?)',
                        (int(club['id']), int(competition['id']),
                         places_booked)
                    )
                db.commit()
                flash('Great-booking complete!')
                return redirect(url_for('booking.show_summary'))

            for message in error:
                flash(message)

        return render_template('booking/booking.html', club=club,
                               competition=competition)

    else:
        flash("Something went wrong-please try again")
        return redirect(url_for('booking.show_summary'))


@bp.route('/points')
def points():
    db = get_db()
    clubs = db.execute(
        'SELECT * FROM clubs'
    ).fetchall()
    return render_template('booking/points.html', clubs=clubs)
