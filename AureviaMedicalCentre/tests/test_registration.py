from conftest import csrf_from

VALID = dict(full_name="Test Person", username="test.person", email="test@example.test",
             phone="555-0199", dob="1990-01-01", gender="Male", blood_group="A+",
             address="1 Example Street", password="Passw0rd123", confirm="Passw0rd123")


def register(client, **overrides):
    data = {**VALID, **overrides, "csrf_token": csrf_from(client, "/register")}
    return client.post("/register", data=data)


def test_registration_succeeds_and_new_user_can_log_in(client):
    assert register(client).status_code == 302
    token = csrf_from(client, "/login")
    r = client.post("/login", data={"username": "test.person", "password": "Passw0rd123", "csrf_token": token})
    assert r.status_code == 302 and r.headers["Location"].endswith("/patient/dashboard")


def test_new_patient_receives_next_sequential_id(client):
    register(client)
    from app.db import get_db
    with client.application.app_context():
        assert get_db().execute("SELECT id FROM patients WHERE email='test@example.test'").fetchone()["id"] == 1007


def test_duplicate_username_rejected(client):
    register(client)
    assert b"already taken" in register(client).data


def test_weak_password_rejected(client):
    assert b"Password must be" in register(client, password="short", confirm="short").data


def test_password_mismatch_rejected(client):
    assert b"do not match" in register(client, confirm="Different123").data


def test_password_is_stored_hashed(client):
    register(client)
    from app.db import get_db
    with client.application.app_context():
        stored = get_db().execute("SELECT password_hash FROM users WHERE username='test.person'").fetchone()[0]
    assert "Passw0rd123" not in stored and stored.startswith(("scrypt:", "pbkdf2:"))


def test_registration_without_csrf_token_is_rejected(client):
    assert client.post("/register", data=VALID).status_code == 400
