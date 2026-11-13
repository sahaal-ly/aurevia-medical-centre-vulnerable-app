# Remediation Guide

## Fix 1 — IDOR: enforce ownership server-side
Vulnerable (current):
```python
@bp.route("/patient/profile/<int:patient_id>")
@login_required
def patient_profile(patient_id):
    p = get_db().execute("SELECT * FROM patients WHERE id=?", (patient_id,)).fetchone()
    if p is None:
        abort(404)
    return render_template("patient_profile.html", p=p)
```
Fixed:
```python
@bp.route("/patient/profile/<int:patient_id>")
@login_required
def patient_profile(patient_id):
    db = get_db()
    p = db.execute("SELECT * FROM patients WHERE id=?", (patient_id,)).fetchone()
    if p is None:
        abort(404)
    # Patients may only see their own record; admins may see any.
    if g.user["role"] == "patient":
        mine = db.execute("SELECT id FROM patients WHERE user_id=?", (g.user["id"],)).fetchone()
        if mine is None or mine["id"] != patient_id:
            abort(404)     # 404 (not 403) avoids confirming that the ID exists
    elif g.user["role"] != "admin":
        abort(403)
    return render_template("patient_profile.html", p=p)
```
Even better: don't take the ID from the client at all — serve `/patient/profile` using `session["user_id"]` (the app already has this as `my_profile`). Also consider non-guessable identifiers (UUIDs), but they are defence-in-depth, not a replacement for the check. Log denied attempts.

## Fix 2 — Vertical privilege escalation: server-side RBAC on every protected route
Vulnerable (current):
```python
@bp.route("/admin/dashboard")
@login_required
def admin_dashboard(): ...
```
Fixed (the app already has this decorator and uses it on the status-update route):
```python
@bp.route("/admin/dashboard")
@role_required("admin")
def admin_dashboard(): ...

@bp.route("/admin/patients")
@role_required("admin")
def admin_patients(): ...

@bp.route("/admin/appointments")
@role_required("admin")
def admin_appointments(): ...
```
`role_required` loads the role from the database via the session user and calls `abort(403)` on mismatch.

Better still — protect a whole area at once:
```python
admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
@admin_bp.before_request
def only_admins():
    if g.user is None or g.user["role"] != "admin":
        abort(403)
```
### Principles
- Deny by default; check authorization on **every** request, on the server.
- Never rely on hiding menu links or URL secrecy.
- Never trust a role/ID sent by the client; derive identity from the session.
- Test with a low-privilege account against every privileged URL, and add automated tests for 401/403/404.
