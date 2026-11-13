"""Authentication helpers: current-user loading and access-control decorators."""
from functools import wraps

from flask import abort, flash, g, redirect, session, url_for

from .db import get_db


def init_app(bp):
    @bp.before_app_request
    def load_current_user():
        g.user = None
        user_id = session.get("user_id")
        if user_id:
            g.user = get_db().execute(
                "SELECT id, username, role, full_name FROM users WHERE id=?", (user_id,)).fetchone()
            if g.user is None:          # stale session (user no longer exists)
                session.clear()


def login_required(view):
    """AUTHENTICATION only: the visitor must be signed in. Does NOT check role or ownership."""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.user is None:
            flash("Please sign in to continue.", "warning")
            return redirect(url_for("main.patient_login"))
        return view(*args, **kwargs)
    return wrapped


def role_required(role):
    """AUTHORIZATION: signed in AND holding `role`, enforced on the server (403 otherwise)."""
    def decorator(view):
        @wraps(view)
        @login_required
        def wrapped(*args, **kwargs):
            if g.user["role"] != role:
                abort(403)
            return view(*args, **kwargs)
        return wrapped
    return decorator


def get_current_patient():
    return get_db().execute("SELECT * FROM patients WHERE user_id=?", (g.user["id"],)).fetchone()


def get_current_doctor():
    return get_db().execute("SELECT * FROM doctors WHERE user_id=?", (g.user["id"],)).fetchone()
