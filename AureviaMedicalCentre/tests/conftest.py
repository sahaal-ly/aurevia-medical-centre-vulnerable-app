"""Shared fixtures: every test gets a fresh, FICTIONAL-data database in a temp dir."""
import re

import pytest

from app import create_app
from app.db import init_db

PATIENT_PASSWORD = "Patient@123"
DOCTOR_PASSWORD = "Doctor@123"
ADMIN_PASSWORD = "Admin@123"


@pytest.fixture()
def app(tmp_path):
    application = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-only-key",
        "DATABASE": str(tmp_path / "test.db"),
    })
    init_db(application)
    return application


@pytest.fixture()
def client(app):
    return app.test_client()


def csrf_from(client, path):
    """Fetch a page and return its CSRF token (also primes the session cookie)."""
    html = client.get(path).get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


def sign_in(client, login_path, username, password):
    token = csrf_from(client, login_path)
    return client.post(login_path, data={"username": username, "password": password, "csrf_token": token})


@pytest.fixture()
def patient_client(app):
    """Client signed in as patient 'aisha' (patient ID 1001)."""
    c = app.test_client()
    assert sign_in(c, "/login", "aisha", PATIENT_PASSWORD).status_code == 302
    return c


@pytest.fixture()
def doctor_client(app):
    c = app.test_client()
    assert sign_in(c, "/doctor/login", "dr.nair", DOCTOR_PASSWORD).status_code == 302
    return c


@pytest.fixture()
def admin_client(app):
    c = app.test_client()
    assert sign_in(c, "/admin/login", "admin", ADMIN_PASSWORD).status_code == 302
    return c
