import functools

from flask import session
from flask import redirect
from flask import url_for


def login_required(view):
    """View decorator that redirects anonymous users to the login page."""

    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get("user_id") is None:
            return redirect(url_for("index"))

        return view(**kwargs)

    return wrapped_view
