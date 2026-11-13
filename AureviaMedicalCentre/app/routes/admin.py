"""Administration area.

INTENTIONAL VULNERABILITY #2 - Vertical Privilege Escalation
Routes: GET /admin/dashboard, /admin/patients, /admin/appointments
These three *view* pages use @login_required (authentication only) instead of
@role_required("admin"), so any signed-in user - including a patient - can open
them by typing the URL. The admin menu is merely hidden from non-admins.
Fix: see Cybersecurity_Assignment_Guide/remediation_guide.md

The state-changing route (POST .../status) is correctly protected.
"""
from flask import abort, flash, redirect, render_template, request, url_for

from . import bp
from ..auth import login_required, role_required
from ..db import get_db
from ..validators import APPOINTMENT_STATUSES


@bp.route("/admin/dashboard")
@login_required                      # <-- INTENTIONALLY missing the admin role check
def admin_dashboard():
    db = get_db()
    count = lambda sql: db.execute(sql).fetchone()[0]
    stats = {
        "patients": count("SELECT COUNT(*) FROM patients"),
        "doctors": count("SELECT COUNT(*) FROM doctors"),
        "appointments": count("SELECT COUNT(*) FROM appointments"),
        "scheduled": count("SELECT COUNT(*) FROM appointments WHERE status='Scheduled'"),
    }
    by_dept = db.execute(
        "SELECT dp.name, COUNT(a.id) AS n FROM departments dp "
        "LEFT JOIN doctors d ON d.department_id = dp.id LEFT JOIN appointments a ON a.doctor_id = d.id "
        "GROUP BY dp.id ORDER BY n DESC").fetchall()
    recent = db.execute(
        "SELECT a.*, p.full_name AS patient, d.full_name AS doctor FROM appointments a "
        "JOIN patients p ON p.id = a.patient_id JOIN doctors d ON d.id = a.doctor_id "
        "ORDER BY a.id DESC LIMIT 6").fetchall()
    return render_template("admin_dashboard.html", stats=stats, by_dept=by_dept, recent=recent)


@bp.route("/admin/patients")
@login_required                      # <-- INTENTIONALLY missing the admin role check
def admin_patients():
    rows = get_db().execute(
        "SELECT p.*, (SELECT COUNT(*) FROM appointments a WHERE a.patient_id = p.id) AS appts "
        "FROM patients p ORDER BY p.id").fetchall()
    return render_template("admin_patients.html", patients=rows)


@bp.route("/admin/appointments")
@login_required                      # <-- INTENTIONALLY missing the admin role check
def admin_appointments():
    rows = get_db().execute(
        "SELECT a.*, p.full_name AS patient, d.full_name AS doctor FROM appointments a "
        "JOIN patients p ON p.id = a.patient_id JOIN doctors d ON d.id = a.doctor_id "
        "ORDER BY a.appt_date DESC, a.appt_time DESC").fetchall()
    return render_template("admin_appointments.html", appts=rows)


@bp.route("/admin/appointments/<int:appt_id>/status", methods=["POST"])
@role_required("admin")              # correctly protected: NOT part of the demonstration
def admin_set_status(appt_id):
    status = request.form.get("status")
    if status not in APPOINTMENT_STATUSES:
        abort(400)
    db = get_db()
    if not db.execute("SELECT 1 FROM appointments WHERE id=?", (appt_id,)).fetchone():
        abort(404)
    db.execute("UPDATE appointments SET status=? WHERE id=?", (status, appt_id))
    db.commit()
    flash("Appointment updated.", "success")
    return redirect(url_for("main.admin_appointments"))
