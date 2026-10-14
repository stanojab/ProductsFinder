"""SQLite cache of fetched ads, keyed by ad ID, so repeat runs don't re-hit the API."""
import json
import sqlite3
from dataclasses import asdict
from datetime import date

from finder.models import Ad

DEFAULT_DB = "ads_cache.db"


def connect(path: str = DEFAULT_DB) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ads (
            ad_id      TEXT PRIMARY KEY,
            data       TEXT NOT NULL,
            fetched_at TEXT NOT NULL DEFAULT (datetime('now'))
        )
    """)
    return conn


def save_ads(conn: sqlite3.Connection, ads: list[Ad]) -> None:
    rows = []
    for ad in ads:
        data = asdict(ad)
        data["start_date"] = ad.start_date.isoformat()
        rows.append((ad.ad_id, json.dumps(data)))
    with conn:
        conn.executemany(
            "INSERT INTO ads (ad_id, data) VALUES (?, ?) "
            "ON CONFLICT(ad_id) DO UPDATE SET data = excluded.data, fetched_at = datetime('now')",
            rows,
        )


def load_ads(conn: sqlite3.Connection, ad_ids: list[str] | None = None) -> list[Ad]:
    if ad_ids is None:
        rows = conn.execute("SELECT data FROM ads").fetchall()
    else:
        placeholders = ",".join("?" * len(ad_ids))
        rows = conn.execute(f"SELECT data FROM ads WHERE ad_id IN ({placeholders})", ad_ids).fetchall()
    ads = []
    for (raw,) in rows:
        data = json.loads(raw)
        data["start_date"] = date.fromisoformat(data["start_date"])
        ads.append(Ad(**data))
    return ads
