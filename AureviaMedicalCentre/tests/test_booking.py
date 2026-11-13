from conftest import csrf_from

FUTURE = "2099-01-15"


def book(client, **overrides):
    data = dict(doctor_id="1", appt_date=FUTURE, appt_time="10:00", reason="Annual check-up")
    data.update(overrides)
    data["csrf_token"] = csrf_from(client, "/patient/book")
    return client.post("/patient/book", data=data)


def test_booking_creates_appointment_visible_in_history(patient_client):
    assert book(patient_client).status_code == 302
    page = patient_client.get("/patient/appointments").data
    assert b"Annual check-up" in page and b"2099-01-15" in page


def test_booking_is_always_attached_to_the_session_patient(patient_client, app):
    """A forged patient_id field in the form is ignored."""
    book(patient_client, patient_id="1002")
    from app.db import get_db
    with app.app_context():
        row = get_db().execute("SELECT patient_id FROM appointments WHERE reason='Annual check-up'").fetchone()
    assert row["patient_id"] == 1001


def test_past_date_rejected(patient_client):
    assert b"cannot be in the past" in book(patient_client, appt_date="2000-01-01").data


def test_invalid_doctor_and_slot_and_reason_rejected(patient_client):
    assert b"valid doctor" in book(patient_client, doctor_id="999").data
    assert b"valid time slot" in book(patient_client, appt_time="03:33").data
    assert b"reason" in book(patient_client, reason="").data


def test_history_shows_only_own_appointments(patient_client):
    page = patient_client.get("/patient/appointments").data
    assert b"Recurring headaches" in page            # Aisha's (1001)
    assert b"Chest discomfort review" not in page    # Rahul's (1002)


def test_booking_requires_login(client):
    assert client.get("/patient/book").status_code == 302
