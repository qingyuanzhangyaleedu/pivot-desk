"""Private local SQLite state scoped to an unguessable browser session."""

import sqlite3, json, secrets, hashlib
from contextlib import contextmanager
from datetime import datetime, timezone
from .config import RUNTIME, ROOT

DB = RUNTIME / "pivot.db"


def now():
    return datetime.now(timezone.utc).isoformat()


@contextmanager
def db():
    con = sqlite3.connect(DB, timeout=15)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA secure_delete=ON")
    try:
        yield con
        con.commit()
    except BaseException:
        con.rollback()
        raise
    finally:
        con.close()


def initialize():
    with db() as c:
        c.executescript("""
        PRAGMA journal_mode=WAL;
        CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS state(session TEXT NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL, PRIMARY KEY(session,key));
        CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS runs(id TEXT PRIMARY KEY, session TEXT NOT NULL, kind TEXT NOT NULL, status TEXT NOT NULL, created TEXT NOT NULL, result TEXT, error TEXT);
        CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, run_id TEXT, session TEXT NOT NULL, agent TEXT NOT NULL, action TEXT NOT NULL, summary TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS usage(id INTEGER PRIMARY KEY, session TEXT NOT NULL, run_id TEXT NOT NULL, input_tokens INTEGER, cached_tokens INTEGER, output_tokens INTEGER, requests INTEGER, cost REAL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS cache(session TEXT NOT NULL, key TEXT NOT NULL, value TEXT NOT NULL, PRIMARY KEY(session,key));
        CREATE TABLE IF NOT EXISTS tracker(session TEXT NOT NULL, job_id TEXT NOT NULL, stage TEXT NOT NULL, note TEXT NOT NULL, follow_up TEXT NOT NULL, updated TEXT NOT NULL, PRIMARY KEY(session,job_id));
        """)
        if not c.execute("SELECT 1 FROM jobs LIMIT 1").fetchone():
            p = ROOT / "data/demo_jobs.json"
            if p.exists():
                for job in json.loads(p.read_text()):
                    c.execute(
                        "INSERT OR IGNORE INTO jobs VALUES (?,?)",
                        (job["id"], json.dumps(job)),
                    )
    try:
        DB.chmod(0o600)
    except OSError:
        pass


def session(existing):
    with db() as c:
        if (
            existing
            and c.execute("SELECT 1 FROM sessions WHERE id=?", (existing,)).fetchone()
        ):
            return existing
        token = secrets.token_urlsafe(32)
        c.execute("INSERT INTO sessions VALUES (?,?)", (token, now()))
        return token


def get(s, key, default=None):
    with db() as c:
        r = c.execute(
            "SELECT value FROM state WHERE session=? AND key=?", (s, key)
        ).fetchone()
    return json.loads(r["value"]) if r else default


def put(s, key, value):
    with db() as c:
        c.execute(
            "INSERT OR REPLACE INTO state VALUES (?,?,?)", (s, key, json.dumps(value))
        )


def event(s, run, agent, action, summary):
    # Callers pass action names/counts, never raw resumes, credentials or sensitive answers.
    with db() as c:
        c.execute(
            "INSERT INTO events(run_id,session,agent,action,summary,created) VALUES (?,?,?,?,?,?)",
            (run, s, agent, action, summary[:300], now()),
        )


def save_jobs(jobs):
    with db() as c:
        for job in jobs:
            c.execute(
                "INSERT OR REPLACE INTO jobs VALUES (?,?)", (job["id"], json.dumps(job))
            )


def job(job_id):
    with db() as c:
        r = c.execute("SELECT payload FROM jobs WHERE id=?", (job_id,)).fetchone()
    return json.loads(r[0]) if r else None


def all_jobs():
    with db() as c:
        return [json.loads(r[0]) for r in c.execute("SELECT payload FROM jobs")]
