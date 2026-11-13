"""Aurevia Medical Centre - Flask application factory."""
from flask import Flask, render_template

from .config import BASE_DIR, build_config
from . import db, security


def create_app(config_overrides=None):
    import os
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, "templates"),
        static_folder=os.path.join(BASE_DIR, "static"),
    )
    app.config.update(build_config(config_overrides))

    db.init_app(app)
    security.init_app(app)

    from .routes import bp
    app.register_blueprint(bp)

    @app.errorhandler(400)
    @app.errorhandler(403)
    @app.errorhandler(404)
    @app.errorhandler(500)
    def show_error_page(error):
        code = getattr(error, "code", 500)
        return render_template("error.html", e=type("E", (), {"code": code})), code

    return app
