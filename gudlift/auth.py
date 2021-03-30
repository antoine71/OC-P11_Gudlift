import functools

from flask import session
from flask import redirect
from flask import url_for
from flask import Blueprint
from flask import request
from flask import flash
from flask import render_template
from flask import g

from gudlift.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/')


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.index"))

        return view(**kwargs)

    return wrapped_view


@bp.route('/', methods=['GET', 'POST'])
def index():
    if request.method == "POST":
        email = request.form["email"]
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM clubs WHERE email = ?', (email,)).fetchone()
        if not email:
            error = "Email is required."
        elif not user:
            error = "The email {0} is not registered.".format(email)

        if error is None:
            session.clear()
            session["user_id"] = email
            return redirect(url_for('booking.show_summary'))

        flash(error)

    return render_template('auth/index.html')


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = user_id


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.index'))
