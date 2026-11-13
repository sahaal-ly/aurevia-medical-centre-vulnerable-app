"""Documents and verifies the TWO deliberate Broken Access Control flaws.

  1. IDOR                         GET /patient/profile/<patient_id>
  2. Vertical privilege escalation GET /admin/dashboard  (+ /admin/patients, /admin/appointments)

These tests PASS because the vulnerabilities exist. After applying the fixes from
Cybersecurity_Assignment_Guide/remediation_guide.md they are expected to FAIL -
that is the point: they prove the flaws were closed.
"""
import pytest


# ---------------------------------------------------------------- 1. IDOR
def test_idor_patient_can_open_own_profile(patient_client):
    r = patient_client.get("/patient/profile", follow_redirects=True)
    assert b"Patient ID 1001" in r.data and b"Aisha Rahman" in r.data


@pytest.mark.parametrize("other_id, name, marker", [
    (1002, b"Rahul Verma", b"Type 2 Diabetes"),
    (1003, b"Meera Pillai", b"Hypertension"),
    (1006, b"Arjun Das", b"Coronary artery disease"),
])
def test_idor_patient_can_read_other_patients_profiles(patient_client, other_id, name, marker):
    """VULNERABLE: aisha (1001) is served another patient's private record."""
    r = patient_client.get(f"/patient/profile/{other_id}")
    assert r.status_code == 200
    assert name in r.data and marker in r.data


def test_idor_unknown_id_returns_404(patient_client):
    assert patient_client.get("/patient/profile/9999").status_code == 404


def test_idor_route_still_requires_authentication(client):
    """Authentication IS enforced - only ownership is missing."""
    assert client.get("/patient/profile/1002").status_code == 302


# ------------------------------------- 2. Vertical privilege escalation
@pytest.mark.parametrize("path, marker", [
    ("/admin/dashboard", b"Hospital Overview"),
    ("/admin/patients", b"Patient Management"),
    ("/admin/appointments", b"Appointment Management"),
])
def test_privilege_escalation_patient_can_open_admin_pages(patient_client, path, marker):
    """VULNERABLE: a plain patient reaches admin pages by typing the URL."""
    r = patient_client.get(path)
    assert r.status_code == 200 and marker in r.data


def test_privilege_escalation_exposes_all_patients(patient_client):
    page = patient_client.get("/admin/patients").data
    for name in (b"Rahul Verma", b"Fatima Noor", b"Arjun Das"):
        assert name in page


def test_privilege_escalation_admin_menu_is_hidden_from_patients(patient_client):
    """The only 'protection' is a hidden link - not access control."""
    assert b"Admin Dashboard" not in patient_client.get("/patient/dashboard").data


def test_admin_pages_still_require_authentication(client):
    for path in ("/admin/dashboard", "/admin/patients", "/admin/appointments"):
        assert client.get(path).status_code == 302
