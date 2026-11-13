from conftest import csrf_from, sign_in


def test_patient_login_and_dashboard(patient_client):
    assert b"Welcome back, Aisha" in patient_client.get("/patient/dashboard").data


def test_wrong_password_rejected(client):
    r = sign_in(client, "/login", "aisha", "wrong-password")
    assert r.status_code == 200 and b"Invalid username or password" in r.data


def test_unknown_user_rejected(client):
    assert b"Invalid username or password" in sign_in(client, "/login", "nobody", "x").data


def test_role_specific_login_forms(client):
    """A patient's credentials do not work on the doctor or admin login forms."""
    assert sign_in(client, "/doctor/login", "aisha", "Patient@123").status_code == 200
    assert sign_in(client, "/admin/login", "aisha", "Patient@123").status_code == 200


def test_doctor_and_admin_login(doctor_client, admin_client):
    assert b"Dr. Anil Nair" in doctor_client.get("/doctor/dashboard").data
    assert b"Hospital Overview" in admin_client.get("/admin/dashboard").data


def test_logout_ends_session(patient_client):
    token = csrf_from(patient_client, "/patient/book")
    assert patient_client.post("/logout", data={"csrf_token": token}).status_code == 302
    assert patient_client.get("/patient/dashboard").status_code == 302   # back to login


def test_logout_requires_post_and_csrf(patient_client):
    assert patient_client.get("/logout").status_code == 405
    assert patient_client.post("/logout").status_code == 400
