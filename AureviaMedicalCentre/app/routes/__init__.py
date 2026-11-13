"""All routes share one blueprint ("main") and are grouped by feature module."""
from flask import Blueprint

from .. import auth

bp = Blueprint("main", __name__)
auth.init_app(bp)

# Importing the modules registers their routes on `bp`.
from . import public, accounts, patient, doctor, admin  # noqa: E402,F401
