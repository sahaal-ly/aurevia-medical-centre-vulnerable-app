"""Example configuration for Aurevia Medical Centre.

Copy to `config.py` (git-ignored) only if you want to override defaults:

    cp config.example.py config.py

Every value can also be supplied through environment variables, which take
precedence. No real secrets belong in this file or in version control.
"""

# Secret used to sign session cookies. Leave as None to have a random key
# generated locally on first run and stored in database/secret.key
# (git-ignored). To set your own:  export AUREVIA_SECRET_KEY="$(python3 -c 'import secrets; print(secrets.token_hex(32))')"
SECRET_KEY = None

# Port to listen on. The server ALWAYS binds to 127.0.0.1 (local machine only).
# Use 80 (requires sudo) to serve at http://aureviamedicalcentre.local
PORT = 5000

# SQLite database location. Created and seeded with FICTIONAL data on first run.
DATABASE = "database/hospital.db"
