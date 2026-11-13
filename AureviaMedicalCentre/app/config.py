"""Application configuration (no secrets are hardcoded here)."""
import os
import secrets

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOST = "127.0.0.1"  # local only - intentionally not configurable


def _load_secret_key():
    """Return the session-signing key: env var, else a locally generated file."""
    env_key = os.environ.get("AUREVIA_SECRET_KEY")
    if env_key:
        return env_key
    path = os.path.join(BASE_DIR, "database", "secret.key")
    if not os.path.exists(path):
        with open(path, "w") as fh:
            fh.write(secrets.token_hex(32))
        os.chmod(path, 0o600)
    with open(path) as fh:
        return fh.read().strip()


def build_config(overrides=None):
    cfg = {
        "SECRET_KEY": None,  # resolved below so tests can inject their own
        "DATABASE": os.environ.get("AUREVIA_DATABASE", os.path.join(BASE_DIR, "database", "hospital.db")),
        "PORT": int(os.environ.get("PORT", "5000")),
        "SESSION_COOKIE_HTTPONLY": True,
        "SESSION_COOKIE_SAMESITE": "Lax",
        "MAX_CONTENT_LENGTH": 64 * 1024,
    }
    cfg.update(overrides or {})
    if not cfg["SECRET_KEY"]:
        cfg["SECRET_KEY"] = _load_secret_key()
    return cfg
