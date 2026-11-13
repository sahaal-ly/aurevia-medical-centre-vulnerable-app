"""Server-side form validation. Each function returns a list of error messages."""
import re
from datetime import date, datetime

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.]{3,30}$")
PHONE_RE = re.compile(r"^[0-9+\-\s]{7,20}$")

TIME_SLOTS = ["09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
              "14:00", "14:30", "15:00", "15:30", "16:00", "16:30"]
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
GENDERS = ("Female", "Male", "Other")
APPOINTMENT_STATUSES = ("Scheduled", "Completed", "Cancelled")

REGISTRATION_FIELDS = ("full_name", "username", "email", "phone", "dob", "gender", "blood_group", "address")


def validate_registration(form, password, confirm):
    errors = []
    if not 2 <= len(form["full_name"]) <= 80:
        errors.append("Please enter your full name.")
    if not USERNAME_RE.match(form["username"]):
        errors.append("Username must be 3-30 characters (letters, digits, . or _).")
    if not EMAIL_RE.match(form["email"]):
        errors.append("Enter a valid email address.")
    if not PHONE_RE.match(form["phone"]):
        errors.append("Enter a valid phone number.")
    try:
        if datetime.strptime(form["dob"], "%Y-%m-%d").date() >= date.today():
            raise ValueError
    except ValueError:
        errors.append("Enter a valid date of birth.")
    if form["gender"] not in GENDERS:
        errors.append("Select a gender.")
    if form["blood_group"] not in BLOOD_GROUPS:
        errors.append("Select a blood group.")
    if not 5 <= len(form["address"]) <= 200:
        errors.append("Enter your address.")
    if len(password) < 8 or not re.search(r"\d", password) or not re.search(r"[A-Za-z]", password):
        errors.append("Password must be 8+ characters with letters and numbers.")
    if password != confirm:
        errors.append("Passwords do not match.")
    return errors


def validate_booking(form, doctor_exists):
    errors = []
    if not form["doctor_id"].isdigit() or not doctor_exists(int(form["doctor_id"])):
        errors.append("Select a valid doctor.")
    try:
        if datetime.strptime(form["appt_date"], "%Y-%m-%d").date() < date.today():
            errors.append("Appointment date cannot be in the past.")
    except ValueError:
        errors.append("Select a valid date.")
    if form["appt_time"] not in TIME_SLOTS:
        errors.append("Select a valid time slot.")
    if not 3 <= len(form["reason"]) <= 200:
        errors.append("Please describe the reason (3-200 characters).")
    return errors
