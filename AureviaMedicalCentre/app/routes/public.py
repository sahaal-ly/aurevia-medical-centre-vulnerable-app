"""Public marketing pages (no authentication required)."""
from flask import render_template

from . import bp
from ..db import get_db

DOCTOR_WITH_DEPT = ("SELECT d.*, dp.name AS dept FROM doctors d "
                    "JOIN departments dp ON dp.id = d.department_id")


@bp.route("/")
def index():
    db = get_db()
    count = lambda table: db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]  # fixed table names only
    return render_template(
        "index.html",
        departments=db.execute("SELECT * FROM departments").fetchall(),
        doctors=db.execute(DOCTOR_WITH_DEPT + " LIMIT 3").fetchall(),
        stats={"doctors": count("doctors"), "patients": count("patients"), "departments": count("departments")},
    )


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/doctors")
def doctors():
    rows = get_db().execute(DOCTOR_WITH_DEPT + " ORDER BY d.full_name").fetchall()
    return render_template("doctors.html", doctors=rows)


@bp.route("/departments")
def departments():
    return render_template("departments.html", departments=get_db().execute("SELECT * FROM departments").fetchall())


@bp.route("/services")
def services():
    return render_template("services.html")
