"""Database utilities for Streamlit app.

This module attempts to connect to Postgres using DB_URL from the
.env file. If Postgres isn't available, it falls back to a local
SQLite file so the UI remains usable for development.
"""
import os
from sqlalchemy import create_engine, text, inspect
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Primary DB URL (Postgres expected). Update via .env if different.
DB_URL = os.getenv("DB_URL", "postgresql://localhost:5432/flightdb")


def _create_engine_with_fallback(db_url: str):
    """Try to create an engine for `db_url`; on failure return a SQLite engine.

    This keeps the Streamlit app usable when Postgres isn't configured.
    """
    try:
        eng = create_engine(db_url, future=True)
        # quick smoke test
        with eng.connect() as conn:
            conn.execute(text("SELECT 1"))
        return eng
    except Exception:
        sqlite_url = os.getenv("SQLITE_FALLBACK", "sqlite:///flightdb.sqlite")
        eng = create_engine(sqlite_url, future=True)
        return eng


# Engine the app will use (Postgres preferred, SQLite fallback)
_engine = _create_engine_with_fallback(DB_URL)
engine = _engine


def get_engine():
    return _engine


def run_query(sql, params=None):
    if params is None:
        params = {}
    with _engine.connect() as conn:
        df = pd.read_sql(sql, conn, params=params)
    return df


def execute(sql, params=None):
    with _engine.begin() as conn:
        result = conn.execute(text(sql), params or {})
        try:
            return result.rowcount
        except Exception:
            return None


def check_schema():
    """Return a list of tables present in the connected database."""
    try:
        inspector = inspect(_engine)
        return inspector.get_table_names()
    except Exception:
        return []

