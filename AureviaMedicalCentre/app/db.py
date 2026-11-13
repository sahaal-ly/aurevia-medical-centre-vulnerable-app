"""SQLite access layer: connection handling, schema and initialisation."""
import os
import sqlite3

from flask import g, current_app

from .seed import seed_database

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('patient','doctor','admin')),
    full_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    icon TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE REFERENCES users(id),
    full_name TEXT NOT NULL,
    department_id INTEGER NOT NULL REFERENCES departments(id),
    qualification TEXT NOT NULL,
    experience INTEGER NOT NULL,
    bio TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY,               -- predictable IDs (1001, 1002, ...)
    user_id INTEGER UNIQUE REFERENCES users(id),
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    dob TEXT NOT NULL,
    gender TEXT NOT NULL,
    blood_group TEXT NOT NULL,
    address TEXT NOT NULL,
    allergies TEXT NOT NULL DEFAULT 'None',
    conditions TEXT NOT NULL DEFAULT 'None'
);
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL REFERENCES patients(id),
    doctor_id INTEGER NOT NULL REFERENCES doctors(id),
    appt_date TEXT NOT NULL,
    appt_time TEXT NOT NULL,
    reason TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Scheduled'
);
"""


def get_db():
    """Per-request connection with row access by column name."""
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def _close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def init_app(app):
    app.teardown_appcontext(_close_db)


def init_db(app, reset=False):
    """Create tables and, on a brand-new database, load FICTIONAL seed data."""
    path = app.config["DATABASE"]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if reset and os.path.exists(path):
        os.remove(path)
    is_new = not os.path.exists(path)
    conn = sqlite3.connect(path)
    try:
        conn.executescript(SCHEMA)
        if is_new:
            seed_database(conn)
        conn.commit()
    finally:
        conn.close()
