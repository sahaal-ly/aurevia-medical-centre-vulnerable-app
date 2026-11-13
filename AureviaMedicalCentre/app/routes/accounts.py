"""Registration, login (patient / doctor / admin) and logout."""
import sqlite3

from flask import flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from . import bp
from ..db import get_db
from ..validators import BLOOD_GROUPS, REGISTRATION_FIELDS, validate_registration


@bp.route("/register", methods=["GET", "POST"])
def register():
    errors, form = [], {}
    if request.method == "POST":
        form = {name: request.form.get(name, "").strip() for name in REGISTRATION_FIELDS}
        password, confirm = request.form.get("password", ""), request.form.get("confirm", "")
        errors = validate_registration(form, password, confirm)
        db = get_db()
        if not errors and db.execute("SELECT 1 FROM users WHERE username=?", (form["username"],)).fetchone():
            errors.append("That username is already taken.")
        if not errors:
            try:
                cur = db.execute("INSERT INTO users(username,password_hash,role,full_name) VALUES (?,?,?,?)",
                                 (form["username"], generate_password_hash(password), "patient", form["full_name"]))
                next_id = (db.execute("SELECT MAX(id) FROM patients").fetchone()[0] or 1000) + 1
                db.execute("INSERT INTO patients(id,user_id,full_name,email,phone,dob,gender,blood_group,address) "
                           "VALUES (?,?,?,?,?,?,?,?,?)",
                           (next_id, cur.lastrowid, form["full_name"], form["email"], form["phone"],
                            form["dob"], form["gender"], form["blood_group"], form["address"]))
                db.commit()
            except sqlite3.IntegrityError:      # lost a race on the unique username
                db.rollback()
                errors.append("That username is already taken.")
            else:
                flash("Registration successful. Please sign in.", "success")
                return redirect(url_for("main.patient_login"))
    return render_template("register.html", errors=errors, form=form, blood=BLOOD_GROUPS)


def _login(role, title, subtitle, destination):
    """Shared login handler. A user may only sign in through the form of their own role."""
    error = None
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = get_db().execute("SELECT * FROM users WHERE username=? AND role=?", (username, role)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()                      # new session on login (prevents session fixation)
            session["user_id"] = user["id"]
            return redirect(url_for(destination))
        error = "Invalid username or password."
    return render_template("login.html", error=error, title=title, subtitle=subtitle, role=role)


@bp.route("/login", methods=["GET", "POST"])
def patient_login():
    return _login("patient", "Patient Login", "Access your appointments and health profile.", "main.patient_dashboard")


@bp.route("/doctor/login", methods=["GET", "POST"])
def doctor_login():
    return _login("doctor", "Doctor Login", "Review your schedule and consultations.", "main.doctor_dashboard")


@bp.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    return _login("admin", "Admin Login", "Hospital administration portal.", "main.admin_dashboard")


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))
