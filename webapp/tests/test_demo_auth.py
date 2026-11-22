"""
tests/test_demo_auth.py
Tests for the SafeParse Demo auth-only application.
Uses Flask's test client with a temp database; never touches demo.db.
"""
import os
import sys
import tempfile
import pytest

# Make D:\SafeParse_demo importable as the package root.
DEMO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if DEMO_ROOT not in sys.path:
    sys.path.insert(0, DEMO_ROOT)

os.environ.setdefault("FLASK_SECRET_KEY", "test-secret-key-not-for-production-32x")

import app as demo_app
import db as demo_db
from db import init_db


@pytest.fixture()
def client(tmp_path):
    db_file = str(tmp_path / "test.db")
    demo_app.app.config["DATABASE"] = db_file
    demo_app.app.config["TESTING"] = True
    demo_app.app.config["WTF_CSRF_ENABLED"] = False

    with demo_app.app.app_context():
        init_db(db_file)
        # Create a test user.
        from db import get_db
        from werkzeug.security import generate_password_hash
        db = get_db(db_file)
        db.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
            ("testadmin", generate_password_hash("correct-password-123"))
        )
        db.commit()

    # Clear rate-limit state between tests.
    demo_app._failed_attempts.clear()

    with demo_app.app.test_client() as c:
        yield c


def _get_csrf(client):
    """Fetch a CSRF token by doing a GET to /login."""
    with client.session_transaction() as sess:
        import secrets
        sess["csrf_token"] = secrets.token_hex(32)
        return sess["csrf_token"]


def _login(client, username="testadmin", password="correct-password-123"):
    csrf = _get_csrf(client)
    return client.post("/login", data={
        "username": username,
        "password": password,
        "csrf_token": csrf,
    }, follow_redirects=True)


# --- Test cases ---

def test_wrong_password_gives_error_no_session(client):
    csrf = _get_csrf(client)
    r = client.post("/login", data={
        "username": "testadmin",
        "password": "wrong-password-xyz",
        "csrf_token": csrf,
    })
    assert b"Invalid username or password" in r.data
    with client.session_transaction() as sess:
        assert "user_id" not in sess


def test_correct_password_reaches_dashboard(client):
    r = _login(client)
    assert r.status_code == 200
    assert b"Dashboard" in r.data or b"SafeParse" in r.data
    with client.session_transaction() as sess:
        assert "user_id" in sess


def test_compile_200_when_logged_in(client):
    _login(client)
    r = client.get("/compile")
    assert r.status_code == 200


def test_history_200_when_logged_in(client):
    _login(client)
    r = client.get("/history")
    assert r.status_code == 200


def test_results_200_when_logged_in(client):
    _login(client)
    r = client.get("/results")
    assert r.status_code == 200


def test_compile_redirects_to_login_when_not_logged_in(client):
    r = client.get("/compile", follow_redirects=False)
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_history_redirects_to_login_when_not_logged_in(client):
    r = client.get("/history", follow_redirects=False)
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_results_redirects_to_login_when_not_logged_in(client):
    r = client.get("/results", follow_redirects=False)
    assert r.status_code == 302
    assert "/login" in r.headers["Location"]


def test_register_returns_404(client):
    r = client.get("/register")
    assert r.status_code == 404


def test_login_post_without_csrf_returns_400(client):
    r = client.post("/login", data={
        "username": "testadmin",
        "password": "correct-password-123",
    })
    assert r.status_code == 400


def test_sixth_wrong_attempt_is_blocked(client):
    for i in range(5):
        csrf = _get_csrf(client)
        client.post("/login", data={
            "username": "testadmin",
            "password": f"wrong-{i}",
            "csrf_token": csrf,
        })
    csrf = _get_csrf(client)
    r = client.post("/login", data={
        "username": "testadmin",
        "password": "still-wrong",
        "csrf_token": csrf,
    })
    assert b"Too many failed attempts" in r.data


def test_logout_clears_session(client):
    _login(client)
    with client.session_transaction() as sess:
        assert "user_id" in sess
        csrf = sess.get("csrf_token", "")
    r = client.post("/logout", data={"csrf_token": csrf}, follow_redirects=True)
    assert r.status_code == 200
    with client.session_transaction() as sess:
        assert "user_id" not in sess
