"""Fictional seed data. No real people, patients or credentials are used.

Demo passwords are intentionally simple, documented in the README and only
meaningful for a local training instance.
"""
from werkzeug.security import generate_password_hash

DEMO_PASSWORDS = {"patient": "Patient@123", "doctor": "Doctor@123", "admin": "Admin@123"}

DEPARTMENTS = [
    ("Cardiology", "Heart care, ECG, echo and preventive cardiac programs.", "bi-heart-pulse"),
    ("Neurology", "Diagnosis and treatment of brain, spine and nerve disorders.", "bi-activity"),
    ("Pediatrics", "Gentle, specialised healthcare for infants and children.", "bi-emoji-smile"),
    ("Orthopedics", "Bone, joint and sports-injury care with modern rehab.", "bi-bandaid"),
    ("General Medicine", "Primary care, health check-ups and chronic disease management.", "bi-clipboard2-pulse"),
]

DOCTORS = [  # username, name, dept(1-based), qualification, years, bio
    ("dr.nair", "Dr. Anil Nair", 1, "MD, DM (Cardiology)", 18, "Interventional cardiologist focused on preventive heart care."),
    ("dr.khan", "Dr. Sana Khan", 2, "MD, DM (Neurology)", 12, "Neurologist specialising in migraine, epilepsy and stroke recovery."),
    ("dr.iyer", "Dr. Priya Iyer", 3, "MD (Pediatrics), DCH", 9, "Paediatrician passionate about child wellness and vaccination."),
    ("dr.menon", "Dr. Rohan Menon", 4, "MS (Orthopaedics)", 14, "Orthopaedic surgeon for joint replacement and sports injuries."),
]

PATIENTS = [  # id, username, name, email, phone, dob, gender, blood, address, allergies, conditions
    (1001, "aisha", "Aisha Rahman", "aisha.rahman@example.test", "555-0101", "1991-03-14", "Female", "O+", "12 Lotus Lane, Riverside", "Penicillin", "Asthma"),
    (1002, "rahul", "Rahul Verma", "rahul.verma@example.test", "555-0102", "1985-07-22", "Male", "A+", "44 Cedar Court, Hillview", "None", "Type 2 Diabetes"),
    (1003, "meera", "Meera Pillai", "meera.pillai@example.test", "555-0103", "1978-11-05", "Female", "B+", "7 Palm Street, Lakeside", "Sulfa drugs", "Hypertension"),
    (1004, "john", "John Mathew", "john.mathew@example.test", "555-0104", "2001-01-30", "Male", "AB-", "98 Maple Avenue, Greenfield", "Peanuts", "None"),
    (1005, "fatima", "Fatima Noor", "fatima.noor@example.test", "555-0105", "1995-09-18", "Female", "O-", "23 Orchid Road, Southgate", "None", "Migraine"),
    (1006, "arjun", "Arjun Das", "arjun.das@example.test", "555-0106", "1969-05-09", "Male", "A-", "5 Willow Way, Northpark", "Latex", "Coronary artery disease"),
]

APPOINTMENTS = [  # patient, doctor(1-based), date, time, reason, status
    (1001, 2, "2026-11-20", "10:00", "Recurring headaches", "Scheduled"),
    (1002, 1, "2026-11-18", "09:30", "Chest discomfort review", "Scheduled"),
    (1003, 1, "2026-11-19", "11:00", "Blood pressure follow-up", "Scheduled"),
    (1004, 4, "2026-11-21", "14:00", "Knee pain after sports", "Scheduled"),
    (1005, 2, "2026-11-12", "10:30", "Migraine consultation", "Completed"),
    (1006, 1, "2026-11-10", "09:00", "Cardiac stress test", "Completed"),
    (1001, 3, "2026-11-05", "16:00", "Child vaccination query", "Completed"),
    (1002, 4, "2026-11-25", "15:30", "Shoulder stiffness", "Scheduled"),
    (1003, 2, "2026-11-08", "12:00", "Dizziness evaluation", "Cancelled"),
    (1006, 1, "2026-11-27", "10:00", "Post-test review", "Scheduled"),
]


def seed_database(conn):
    cur = conn.cursor()
    cur.executemany("INSERT INTO departments(name,description,icon) VALUES (?,?,?)", DEPARTMENTS)

    def add_user(username, role, full_name):
        cur.execute("INSERT INTO users(username,password_hash,role,full_name) VALUES (?,?,?,?)",
                    (username, generate_password_hash(DEMO_PASSWORDS[role]), role, full_name))
        return cur.lastrowid

    add_user("admin", "admin", "Hospital Administrator")
    for username, name, dept, qualification, years, bio in DOCTORS:
        user_id = add_user(username, "doctor", name)
        cur.execute("INSERT INTO doctors(user_id,full_name,department_id,qualification,experience,bio) VALUES (?,?,?,?,?,?)",
                    (user_id, name, dept, qualification, years, bio))
    for pid, username, name, email, phone, dob, gender, blood, address, allergies, conditions in PATIENTS:
        user_id = add_user(username, "patient", name)
        cur.execute("INSERT INTO patients(id,user_id,full_name,email,phone,dob,gender,blood_group,address,allergies,conditions) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (pid, user_id, name, email, phone, dob, gender, blood, address, allergies, conditions))
    cur.executemany("INSERT INTO appointments(patient_id,doctor_id,appt_date,appt_time,reason,status) VALUES (?,?,?,?,?,?)", APPOINTMENTS)
