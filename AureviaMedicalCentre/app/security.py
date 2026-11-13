"""CSRF protection for every state-changing (POST) request."""
import secrets

from flask import abort, request, session


def init_app(app):
    @app.before_request
    def verify_csrf_token():
        if request.method == "POST":
            expected = session.get("_csrf", "")
            supplied = request.form.get("csrf_token", "")
            if not expected or not secrets.compare_digest(expected, supplied):
                abort(400)

    @app.context_processor
    def expose_csrf_token():
        def csrf_token():
            if "_csrf" not in session:
                session["_csrf"] = secrets.token_hex(16)
            return session["_csrf"]
        return {"csrf_token": csrf_token}
