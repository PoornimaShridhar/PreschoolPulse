import json
import sqlite3
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from data.sample_data import build_demo_snapshot, build_demo_leads


SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source TEXT NOT NULL,
    payload TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact TEXT NOT NULL,
    source TEXT NOT NULL,
    stage TEXT NOT NULL,
    notes TEXT NOT NULL,
    created_at TEXT NOT NULL
);
"""


def _connect(database_path: Path) -> sqlite3.Connection:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database(database_path: Path) -> None:
    with _connect(database_path) as connection:
        connection.executescript(SCHEMA)


def seed_demo_content(database_path: Path) -> None:
    with _connect(database_path) as connection:
        snapshot_count = connection.execute("SELECT COUNT(*) FROM snapshots").fetchone()[0]
        lead_count = connection.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        if snapshot_count == 0:
            snapshot = build_demo_snapshot()
            connection.execute(
                "INSERT INTO snapshots (source, payload, created_at) VALUES (?, ?, ?)",
                (snapshot["source"], json.dumps(snapshot), snapshot["created_at"]),
            )
        if lead_count == 0:
            for lead in build_demo_leads():
                lead_data = asdict(lead) if is_dataclass(lead) else lead
                connection.execute(
                    """
                    INSERT INTO leads (name, contact, source, stage, notes, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        lead_data["name"],
                        lead_data.get("contact", ""),
                        lead_data["source"],
                        lead_data["stage"],
                        lead_data.get("notes", ""),
                        lead_data.get("created_at", datetime.now(timezone.utc).isoformat()),
                    ),
                )
        connection.commit()


def save_snapshot(database_path: Path, source: str, payload: dict[str, Any]) -> None:
    with _connect(database_path) as connection:
        connection.execute(
            "INSERT INTO snapshots (source, payload, created_at) VALUES (?, ?, ?)",
            (source, json.dumps(payload), datetime.now(timezone.utc).isoformat()),
        )
        connection.commit()


def add_lead(database_path: Path, lead: dict[str, str]) -> None:
    with _connect(database_path) as connection:
        connection.execute(
            """
            INSERT INTO leads (name, contact, source, stage, notes, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                lead["name"],
                lead["contact"],
                lead["source"],
                lead["stage"],
                lead["notes"],
                lead.get("created_at", datetime.now(timezone.utc).isoformat()),
            ),
        )
        connection.commit()


def list_leads(database_path: Path) -> list[dict[str, Any]]:
    with _connect(database_path) as connection:
        rows = connection.execute(
            "SELECT name, contact, source, stage, notes, created_at FROM leads ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def list_snapshots(database_path: Path) -> list[dict[str, Any]]:
    with _connect(database_path) as connection:
        rows = connection.execute(
            "SELECT source, payload, created_at FROM snapshots ORDER BY id DESC"
        ).fetchall()
    snapshots: list[dict[str, Any]] = []
    for row in rows:
        payload = json.loads(row["payload"])
        payload["source"] = row["source"]
        payload["created_at"] = row["created_at"]
        snapshots.append(payload)
    return snapshots
