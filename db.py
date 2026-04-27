import sqlite3
from datetime import date
from pathlib import Path

DB_PATH = Path(__file__).parent / "attendance.db"


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS attendance (
            date TEXT PRIMARY KEY,
            clock_in_at TEXT,
            clock_out_at TEXT
        )
        """
    )
    conn.commit()
    return conn


def is_clocked_in(target_date: date | None = None) -> bool:
    d = (target_date or date.today()).isoformat()
    conn = _get_conn()
    row = conn.execute(
        "SELECT clock_in_at FROM attendance WHERE date = ?", (d,)
    ).fetchone()
    conn.close()
    return row is not None and row[0] is not None


def is_clocked_out(target_date: date | None = None) -> bool:
    d = (target_date or date.today()).isoformat()
    conn = _get_conn()
    row = conn.execute(
        "SELECT clock_out_at FROM attendance WHERE date = ?", (d,)
    ).fetchone()
    conn.close()
    return row is not None and row[0] is not None


def record_clock_in(target_date: date | None = None) -> None:
    from datetime import datetime

    d = (target_date or date.today()).isoformat()
    now = datetime.now().isoformat()
    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO attendance (date, clock_in_at)
        VALUES (?, ?)
        ON CONFLICT(date) DO UPDATE SET clock_in_at = ?
        """,
        (d, now, now),
    )
    conn.commit()
    conn.close()


def record_clock_out(target_date: date | None = None) -> None:
    from datetime import datetime

    d = (target_date or date.today()).isoformat()
    now = datetime.now().isoformat()
    conn = _get_conn()
    conn.execute(
        """
        INSERT INTO attendance (date, clock_out_at)
        VALUES (?, ?)
        ON CONFLICT(date) DO UPDATE SET clock_out_at = ?
        """,
        (d, now, now),
    )
    conn.commit()
    conn.close()
