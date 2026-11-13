"""Patient area: dashboard, profile, booking and appointment history."""
from datetime import date

from flask import abort, flash, redirect, render_template, request, url_for

from . import bp
from ..auth import get_current_patient, login_required, role_required
from ..db import get_db
from ..validators import TIME_SLOTS, validate_booking

APPOINTMENT_WITH_DOCTOR = (
    "SELECT a.*, d.full_name AS doctor, dp.name AS dept FROM appointments a "
    "JOIN doctors d ON d.id = a.doctor_id JOIN departments dp ON dp.id = d.department_id ")


@bp.route("/patient/dashboard")
@role_required("patient")
def patient_dashboard():
    db = get_db()
    patient = get_current_patient()
    upcoming = db.execute(APPOINTMENT_WITH_DOCTOR +
                          "WHERE a.patient_id=? AND a.status='Scheduled' "
                          "ORDER BY a.appt_date, a.appt_time LIMIT 3", (patient["id"],)).fetchall()
    total = db.execute("SELECT COUNT(*) FROM appointments WHERE patient_id=?", (patient["id"],)).fetchone()[0]
    return render_template("patient_dashboard.html", p=patient, upcoming=upcoming, total=total)


@bp.route("/patient/profile")
@role_required("patient")
def my_profile():
    """Convenience redirect to the signed-in patient's own profile URL."""
    return redirect(url_for("main.patient_profile", patient_id=get_current_patient()["id"]))


# =====================================================================
# INTENTIONAL VULNERABILITY #1 - IDOR (Insecure Direct Object Reference)
# Route: GET /patient/profile/<patient_id>
# The visitor is authenticated (@login_required) but the record is looked up
# purely by the ID in the URL. There is NO ownership check, so any signed-in
# user can read any patient's profile by changing the number.
# Fix: see Cybersecurity_Assignment_Guide/remediation_guide.md
# =====================================================================
@bp.route("/patient/profile/<int:patient_id>")
@login_required
def patient_profile(patient_id):
    patient = get_db().execute("SELECT * FROM patients WHERE id=?", (patient_id,)).fetchone()
    if patient is None:
        abort(404)
    return render_template("patient_profile.html", p=patient)


@bp.route("/patient/book", methods=["GET", "POST"])
@role_required("patient")
def book():
    db = get_db()
    patient = get_current_patient()
    doctors = db.execute("SELECT d.id, d.full_name, dp.name AS dept FROM doctors d "
                         "JOIN departments dp ON dp.id = d.department_id ORDER BY dp.name").fetchall()
    errors, form = [], {}
    if request.method == "POST":
        form = {k: request.form.get(k, "").strip() for k in ("doctor_id", "appt_date", "appt_time", "reason")}
        doctor_exists = lambda doctor_id: db.execute("SELECT 1 FROM doctors WHERE id=?", (doctor_id,)).fetchone()
        errors = validate_booking(form, doctor_exists)
        if not errors:
            # The patient is always taken from the session, never from the form.
            db.execute("INSERT INTO appointments(patient_id,doctor_id,appt_date,appt_time,reason,status) "
                       "VALUES (?,?,?,?,?,'Scheduled')",
                       (patient["id"], int(form["doctor_id"]), form["appt_date"], form["appt_time"], form["reason"]))
            db.commit()
            flash("Your appointment has been booked.", "success")
            return redirect(url_for("main.history"))
    return render_template("book.html", doctors=doctors, slots=TIME_SLOTS, errors=errors,
                           form=form, today=date.today().isoformat())


@bp.route("/patient/appointments")
@role_required("patient")
def history():
    rows = get_db().execute(APPOINTMENT_WITH_DOCTOR + "WHERE a.patient_id=? "
                            "ORDER BY a.appt_date DESC, a.appt_time DESC", (get_current_patient()["id"],)).fetchall()
    return render_template("history.html", appts=rows)
