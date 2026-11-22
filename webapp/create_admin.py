import os
import sys
import sqlite3
import getpass
from werkzeug.security import generate_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo.db")
SCHEMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "schema.sql")


def init_db(conn):
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())
    conn.commit()


def main():
    username = input("Enter admin username: ").strip()
    if not username:
        print("Username cannot be empty.")
        sys.exit(1)

    password = getpass.getpass("Enter password (min 12 characters): ")
    if len(password) < 12:
        print("Password must be at least 12 characters.")
        sys.exit(1)

    password2 = getpass.getpass("Confirm password: ")
    if password != password2:
        print("Passwords do not match.")
        sys.exit(1)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    init_db(conn)

    existing = conn.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    if existing is not None:
        print(f"Username '{username}' already exists. Aborting.")
        conn.close()
        sys.exit(1)

    hashed = generate_password_hash(password)
    conn.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
        (username, hashed)
    )
    conn.commit()
    conn.close()
    print(f"Admin user '{username}' created successfully.")


if __name__ == "__main__":
    main()
