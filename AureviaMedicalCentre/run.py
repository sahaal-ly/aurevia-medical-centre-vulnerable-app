"""Aurevia Medical Centre - local launcher.

Always binds to 127.0.0.1. Set PORT=80 (and use sudo) to drop the port number.
"""
from app import create_app
from app.config import HOST
from app.db import init_db

app = create_app()

if __name__ == "__main__":
    init_db(app)
    app.run(host=HOST, port=app.config["PORT"], debug=False)
