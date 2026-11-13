"""Everything that is NOT one of the two intentional flaws must enforce access control."""
import pytest

from conftest import csrf_from


@pytest.mark.parametrize("path", [
    "/patient/dashboard", "/patient/profile", "/patient/book", "/patient/appointments",
    "/doctor/dashboard",
])
def test_protected_pages_redirect_anonymous_users(client, path):
    assert client.get(path).status_code == 302


def test_patient_cannot_open_doctor_dashboard(patient_client):
    assert patient_client.get("/doctor/dashboard").status_code == 403


@pytest.mark.parametrize("path", ["/patient/dashboard", "/patient/book", "/patient/appointments", "/patient/profile"])
def test_doctor_and_admin_cannot_use_patient_only_pages(doctor_client, admin_client, path):
    assert doctor_client.get(path).status_code == 403
    assert admin_client.get(path).status_code == 403


def test_patient_cannot_change_appointment_status(patient_client):
    """The admin WRITE route is properly protected (only the admin VIEW pages are vulnerable)."""
    token = csrf_from(patient_client, "/patient/book")
    r = patient_client.post("/admin/appointments/1/status", data={"status": "Cancelled", "csrf_token": token})
    assert r.status_code == 403


def test_admin_can_change_appointment_status(admin_client, app):
    token = csrf_from(admin_client, "/admin/appointments")
    r = admin_client.post("/admin/appointments/1/status", data={"status": "Completed", "csrf_token": token})
    assert r.status_code == 302
    from app.db import get_db
    with app.app_context():
        assert get_db().execute("SELECT status FROM appointments WHERE id=1").fetchone()[0] == "Completed"


def test_invalid_status_rejected(admin_client):
    token = csrf_from(admin_client, "/admin/appointments")
    assert admin_client.post("/admin/appointments/1/status", data={"status": "Hacked", "csrf_token": token}).status_code == 400


def test_post_without_csrf_token_rejected(admin_client):
    assert admin_client.post("/admin/appointments/1/status", data={"status": "Completed"}).status_code == 400


def test_doctor_sees_only_own_appointments(doctor_client):
    page = doctor_client.get("/doctor/dashboard").data       # Dr. Nair (doctor 1)
    assert b"Chest discomfort review" in page
    assert b"Recurring headaches" not in page                # belongs to Dr. Khan


def test_sql_injection_attempt_in_login_fails(client):
    from conftest import sign_in
    assert sign_in(client, "/login", "' OR '1'='1' --", "x").status_code == 200


def test_session_cookie_flags(patient_client, app):
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"


def test_server_binds_to_loopback_only():
    from app.config import HOST
    assert HOST == "127.0.0.1"


def test_unknown_page_returns_404(client):
    assert client.get("/no-such-page").status_code == 404


def test_public_pages_load(client):
    for path in ("/", "/about", "/doctors", "/departments", "/services", "/register", "/login",
                 "/doctor/login", "/admin/login"):
        assert client.get(path).status_code == 200, path
