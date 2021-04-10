import sqlite3

import pytest
from gudlift.db import get_db
from gudlift.db import populate_db, init_db


def test_get_close_db(app):
    with app.app_context():
        db = get_db()
        assert db is get_db()

    with pytest.raises(sqlite3.ProgrammingError) as e:
        db.execute('SELECT 1')

    assert 'closed' in str(e.value)


def test_populate_db(app):
    with app.app_context():
        with pytest.raises(
                Exception,
                match='The database is not empty, please intialize it first.'):
            populate_db()

    with app.app_context():
        init_db()
        populate_db()
        db = get_db()
        assert db.execute('SELECT COUNT(*) FROM clubs').fetchone()[0] == 3
        assert db.execute(
            'SELECT COUNT(*) FROM competitions').fetchone()[0] == 2


def test_init_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_init_db():
        Recorder.called = True

    monkeypatch.setattr('gudlift.db.init_db', fake_init_db)
    result = runner.invoke(args=['init-db'])
    assert 'Initialized' in result.output
    assert Recorder.called


def test_populate_db_command(runner, monkeypatch):
    class Recorder(object):
        called = False

    def fake_populate_db():
        Recorder.called = True

    monkeypatch.setattr('gudlift.db.populate_db', fake_populate_db)
    result = runner.invoke(args=['populate-db'])
    assert 'Populated' in result.output
    assert Recorder.called
