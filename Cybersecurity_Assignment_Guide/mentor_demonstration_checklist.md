# Mentor Demonstration Checklist

**Before you start**
- [ ] Hosts entry present (`ping aureviamedicalcentre.local`)
- [ ] `python run.py` running; open http://aureviamedicalcentre.local:5000
- [ ] Fresh DB if needed: `rm database/hospital.db && python run.py`
- [ ] Two browser windows ready (normal + private)

## 1. Introduce the hospital website (2 min)
- [ ] Tour: Home, About, Doctors, Departments, Services
- [ ] Mention stack (Flask, SQLite, Bootstrap, sessions, CSRF, hashed passwords)
- [ ] Show Register page working

## 2. Normal patient login (1 min)
- [ ] Log in as `aisha` / `Patient@123`
- [ ] Show dashboard, booking an appointment, appointment history
- [ ] Point out the navbar has no admin options

## 3. IDOR demo (3 min)
- [ ] My Profile → note URL `/patient/profile/1001`
- [ ] Change to `1002`, then `1006`
- [ ] Show Rahul's / Arjun's medical data on screen
- [ ] State: logged-in ≠ authorized; server never checks ownership

## 4. Vertical privilege escalation demo (3 min)
- [ ] Log in as `john` / `Patient@123`
- [ ] Manually open `/admin/dashboard`, then `/admin/patients`, `/admin/appointments`
- [ ] Show that the status-change POST is still blocked (403) — highlight the missing check on the *view* routes only

## 5. Security impact (2 min)
- [ ] Patient privacy / health-data breach, mass enumeration, regulatory exposure (HIPAA/GDPR)
- [ ] Admin data leak, reconnaissance for further attacks
- [ ] OWASP Top 10 A01:2021 Broken Access Control

## 6. Remediation (3 min)
- [ ] Ownership check / 404 for IDOR
- [ ] `@role_required("admin")` on every admin route; deny by default
- [ ] Show the corrected code from `remediation_guide.md`

**Wrap-up:** stop server (`Ctrl+C`), optionally remove hosts entry.
