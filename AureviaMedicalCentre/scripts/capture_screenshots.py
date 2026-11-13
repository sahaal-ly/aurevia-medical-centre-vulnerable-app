"""Capture README screenshots from a RUNNING local instance (synthetic data only).

Optional developer tool - not needed to run the app.
    pip install playwright          # drives your installed Google Chrome
    python run.py                   # in another terminal (fresh database recommended)
    python scripts/capture_screenshots.py [base_url] [output_dir]
"""
import os
import sys

from playwright.sync_api import sync_playwright

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://aureviamedicalcentre.local:5000"
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(os.path.dirname(__file__), "..", "..", "screenshots")


def sign_in(page, path, username, password):
    page.goto(BASE + path)
    page.fill("input[name=username]", username)
    page.fill("input[name=password]", password)
    page.click("button.btn-brand")
    page.wait_for_load_state("networkidle")


def shot(page, name):
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(900)           # let entrance animations finish
    page.screenshot(path=os.path.join(OUT, name))
    print("saved", name)


with sync_playwright() as pw:
    browser = pw.chromium.launch(channel="chrome")
    ctx = browser.new_context(viewport={"width": 1366, "height": 820})
    page = ctx.new_page()

    page.goto(BASE + "/");          shot(page, "01-homepage.png")
    page.goto(BASE + "/doctors");   shot(page, "02-doctors-directory.png")
    page.goto(BASE + "/login");     shot(page, "03-patient-login.png")

    sign_in(page, "/login", "aisha", "Patient@123")
    shot(page, "04-patient-dashboard.png")
    page.goto(BASE + "/patient/book")
    page.select_option("select[name=doctor_id]", index=1)
    page.fill("input[name=appt_date]", "2026-12-20")
    page.fill("textarea[name=reason]", "Routine health check-up")
    shot(page, "05-appointment-booking.png")

    # Vulnerability 1 (IDOR): signed in as Aisha (patient 1001) but viewing patient 1002
    page.goto(BASE + "/patient/profile/1002")
    shot(page, "07-idor-demonstration.png")
    ctx.clear_cookies()

    # Vulnerability 2 (privilege escalation): a normal patient opens the admin dashboard
    sign_in(page, "/login", "john", "Patient@123")
    page.goto(BASE + "/admin/dashboard")
    shot(page, "08-privilege-escalation-demonstration.png")
    ctx.clear_cookies()

    # The same page as its legitimate admin user
    sign_in(page, "/admin/login", "admin", "Admin@123")
    page.goto(BASE + "/admin/dashboard")
    shot(page, "06-admin-dashboard.png")
    browser.close()
