import sqlite3
import os
from flask import g, current_app, has_app_context

SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "schema.sql")
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo.db")


def get_db(db_path=None):
    if has_app_context():
        if "db" not in g:
            target_path = db_path or current_app.config.get("DATABASE", DEFAULT_DB_PATH)
            connection = sqlite3.connect(target_path)
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON;")
            g.db = connection
        return g.db
    target_path = db_path or DEFAULT_DB_PATH
    connection = sqlite3.connect(target_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def close_db(error=None):
    if has_app_context():
        connection = g.pop("db", None)
        if connection is not None:
            connection.close()


def init_db(db_path=None):
    with open(SCHEMA_PATH, "r") as f:
        schema_sql = f.read()
    connection = get_db(db_path)
    connection.executescript(schema_sql)
    connection.commit()
    if not has_app_context():
        connection.close()
