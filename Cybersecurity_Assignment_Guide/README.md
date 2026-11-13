# Aurevia Medical Centre — Private Cybersecurity Assignment Guide

> This guide lives outside the Flask app directory, so the website never serves it (no route, static file or page exposes it).
> The hospital app is **intentionally vulnerable**. Run it on `127.0.0.1` only. Never deploy it.

## Overview
A hospital website (Flask + SQLite + Bootstrap 5) with exactly two deliberate Broken Access Control flaws:
1. **IDOR** on `/patient/profile/<patient_id>`
2. **Vertical privilege escalation** on `/admin/dashboard` (and the two admin view pages)

All data is fictional. Everything else (CSRF, hashed passwords, parameterised SQL, role checks) is implemented securely.

## Stack
Python Flask · SQLite · Flask sessions · Werkzeug password hashing · Bootstrap 5 (CDN, needs internet for CSS/fonts) · manual CSRF tokens.

## Layout
```
AureviaMedicalProject/
├── AureviaMedicalCentre/            <- the website (Flask app)
│   ├── app/ (routes/, auth.py, db.py, seed.py, validators.py, security.py, config.py)
│   ├── templates/  static/  database/  tests/
│   └── requirements.txt  config.example.py  run.py
├── Cybersecurity_Assignment_Guide/  <- this private guide (outside the website)
└── screenshots/
```

## Install & run (macOS Apple Silicon or Kali)
```bash
cd AureviaMedicalProject/AureviaMedicalCentre
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py          # creates + seeds database/hospital.db on first run
```
Open: **http://aureviamedicalcentre.local:5000**

To drop the port number (serve on port 80, needs sudo to bind a low port):
```bash
sudo env PORT=80 ./venv/bin/python run.py
```
Then open **http://aureviamedicalcentre.local**

Stop: press `Ctrl+C`, or `pkill -f run.py`.
Reset data: `rm database/hospital.db && python run.py`
Run the tests: `pip install -r requirements-dev.txt && pytest`

## Local domain (hosts file)
macOS:
```bash
echo "127.0.0.1 aureviamedicalcentre.local" | sudo tee -a /etc/hosts
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
```
Kali Linux:
```bash
echo "127.0.0.1 aureviamedicalcentre.local" | sudo tee -a /etc/hosts
```
Verify: `ping -c1 aureviamedicalcentre.local`
Remove later: delete that line from `/etc/hosts`.

Note: the server binds to `127.0.0.1`, so it is reachable only from this machine.

## Sample credentials (all fictional)
| Role | Username | Password | Notes |
|---|---|---|---|
| Patient | `aisha` | `Patient@123` | Patient ID **1001** |
| Patient | `rahul` | `Patient@123` | ID 1002 |
| Patient | `meera` | `Patient@123` | ID 1003 |
| Patient | `john` | `Patient@123` | ID 1004 |
| Patient | `fatima` | `Patient@123` | ID 1005 |
| Patient | `arjun` | `Patient@123` | ID 1006 |
| Doctor | `dr.nair`, `dr.khan`, `dr.iyer`, `dr.menon` | `Doctor@123` | |
| Admin | `admin` | `Admin@123` | |

Other files: `vulnerability_analysis.md`, `exploitation_walkthrough.md`, `remediation_guide.md`, `mentor_demonstration_checklist.md`.
