"""Doctor area (role enforced on the server)."""
from flask import render_template

from . import bp
from ..auth import get_current_doctor, role_required
from ..db import get_db


@bp.route("/doctor/dashboard")
@role_required("doctor")
def doctor_dashboard():
    doctor = get_current_doctor()
    appointments = get_db().execute(
        "SELECT a.*, p.full_name AS patient, p.gender, p.blood_group FROM appointments a "
        "JOIN patients p ON p.id = a.patient_id WHERE a.doctor_id=? "
        "ORDER BY a.appt_date, a.appt_time", (doctor["id"],)).fetchall()
    return render_template("doctor_dashboard.html", doc=doctor, appts=appointments)
