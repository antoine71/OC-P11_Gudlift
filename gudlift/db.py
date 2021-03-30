import sqlite3
import click
import json
from datetime import datetime


from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


def populate_db():
    db = get_db()

    # check that the the database is empty
    clubs = db.execute('SELECT * FROM clubs').fetchall()
    competitions = db.execute('SELECT * FROM competitions').fetchall()

    if clubs and competitions:
        raise Exception("The database is not empty, please intialize it first.")

    with open('gudlift/json/clubs.json') as f:
        list_of_clubs = json.load(f)['clubs']

    with open('gudlift/json/competitions.json') as f:
        list_of_competitions = json.load(f)['competitions']

    for club in list_of_clubs:
        db.execute("INSERT INTO clubs (name, email, points) VALUES (?, ?, ?)",
                   (club['name'], club['email'], club['points']))

    for competition in list_of_competitions:
        db.execute("INSERT INTO competitions (name, date, number_of_places)"
                   "VALUES (?, ?, ?)",
                   (competition['name'],
                    datetime.fromisoformat(competition['date']),
                    int(competition['number_of_places'])
                    ))
    db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


@click.command('populate-db')
@with_appcontext
def populate_db_command():
    """Populate tables from json files."""
    populate_db()
    click.echo('Populated the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(populate_db_command)
