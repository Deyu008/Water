from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import cast

from .core.paths import get_db_path


class Database:
    def __init__(self, db_path: Path | str | None = None):
        self.db_path: Path = Path(db_path) if db_path is not None else get_db_path()
        _ = self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: sqlite3.Connection = sqlite3.connect(str(self.db_path), timeout=5.0)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self._init_db()

    def _init_db(self) -> None:
        _ = self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS intake (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts_utc INTEGER NOT NULL,
                amount_ml INTEGER NOT NULL,
                source TEXT DEFAULT 'button'
            )
            """
        )
        _ = self.conn.execute("CREATE INDEX IF NOT EXISTS idx_intake_ts ON intake(ts_utc)")
        _ = self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS meta (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )
        _ = self.conn.execute(
            "INSERT OR IGNORE INTO meta(key, value) VALUES(?, ?)",
            ("schema_version", "1"),
        )
        self.conn.commit()

    def add_intake(self, amount_ml: int, source: str = "button") -> int:
        amount_value = int(amount_ml)
        if amount_value <= 0:
            raise ValueError("amount_ml must be positive")

        source_value = source if source in {"button", "manual", "tray", "reminder"} else "button"
        ts_utc = int(datetime.now(timezone.utc).timestamp())
        cur = self.conn.execute(
            "INSERT INTO intake(ts_utc, amount_ml, source) VALUES(?, ?, ?)",
            (ts_utc, amount_value, source_value),
        )
        self.conn.commit()
        last_id = cur.lastrowid
        return int(last_id) if last_id is not None else 0

    def delete_intake(self, intake_id: int) -> bool:
        cur = self.conn.execute("DELETE FROM intake WHERE id = ?", (int(intake_id),))
        self.conn.commit()
        return cur.rowcount > 0

    def get_today_total(self) -> int:
        now_local = datetime.now().astimezone()
        start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        end_local = start_local + timedelta(days=1)

        start_utc = int(start_local.astimezone(timezone.utc).timestamp())
        end_utc = int(end_local.astimezone(timezone.utc).timestamp())

        cursor = self.conn.execute(
            "SELECT COALESCE(SUM(amount_ml), 0) AS total_ml FROM intake WHERE ts_utc >= ? AND ts_utc < ?",
            (start_utc, end_utc),
        )
        row = cast(sqlite3.Row | None, cursor.fetchone())
        if row is None:
            return 0
        return int(cast(int, row["total_ml"]))

    def get_daily_totals(self, days: int = 7) -> list[dict[str, str | int]]:
        days_value = int(days)
        if days_value <= 0:
            return []

        now_local = datetime.now().astimezone()
        today_start_local = now_local.replace(hour=0, minute=0, second=0, microsecond=0)
        start_local = today_start_local - timedelta(days=days_value - 1)
        end_local = today_start_local + timedelta(days=1)

        start_utc = int(start_local.astimezone(timezone.utc).timestamp())
        end_utc = int(end_local.astimezone(timezone.utc).timestamp())

        cursor = self.conn.execute(
            "SELECT ts_utc, amount_ml FROM intake WHERE ts_utc >= ? AND ts_utc < ? ORDER BY ts_utc ASC",
            (start_utc, end_utc),
        )
        rows = cast(list[sqlite3.Row], cursor.fetchall())

        ordered_dates: list[str] = []
        totals: dict[str, int] = {}
        for i in range(days_value):
            day = (start_local + timedelta(days=i)).date().isoformat()
            ordered_dates.append(day)
            totals[day] = 0

        for row in rows:
            ts_value = cast(int, row["ts_utc"])
            amount_value = cast(int, row["amount_ml"])
            local_day = datetime.fromtimestamp(ts_value, tz=timezone.utc).astimezone().date().isoformat()
            if local_day in totals:
                totals[local_day] += int(amount_value)

        return [{"date": day, "total_ml": totals[day]} for day in ordered_dates]

    def get_recent(self, n: int = 20) -> list[dict[str, str | int]]:
        n_value = int(n)
        if n_value <= 0:
            return []

        cursor = self.conn.execute(
            "SELECT id, ts_utc, amount_ml, source FROM intake ORDER BY ts_utc DESC, id DESC LIMIT ?",
            (n_value,),
        )
        rows = cast(list[sqlite3.Row], cursor.fetchall())

        recent: list[dict[str, str | int]] = []
        for row in rows:
            row_id = cast(int, row["id"])
            ts_value = cast(int, row["ts_utc"])
            amount_value = cast(int, row["amount_ml"])
            source_value = cast(str, row["source"])
            local_time = datetime.fromtimestamp(ts_value, tz=timezone.utc).astimezone().strftime("%H:%M")
            recent.append(
                {
                    "id": int(row_id),
                    "time": local_time,
                    "amount_ml": int(amount_value),
                    "source": source_value,
                }
            )
        return recent

    def close(self) -> None:
        if self.conn:
            self.conn.close()
