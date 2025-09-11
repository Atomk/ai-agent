import sqlite3
from datetime import datetime, timezone

from google.genai import types
from pydantic import BaseModel, Field

import config

def _now() -> str:
    """Returns the current UTC time in the following format:
        YYYY-MM-DD HH:MM:SS.SSS
    Number of subseconds digit may vary.
    """
    return datetime_to_utc_string(datetime.now())


def datetime_to_utc_string(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime(r"%F %T.%f")


class Record(BaseModel):
    """Represents data for a single request, to be stored in the database.

    If 'ts' is not specified, current UTC time will be used.
    """
    ts: str = Field(
        pattern=r"\d{4}-[01]\d-[0-3]\d \d{2}:\d{2}:\d{2}.\d{3}",
        default_factory=_now
    )
    conversation_id: int | None = None
    tokens_prompt: int
    tokens_candidates: int
    # Computed field, can delete column
    tokens_total: int


class Database:
    def __init__(self, db_name) -> None:
        self._db_name = db_name
        with sqlite3.connect(self._db_name) as connection:
            cur = connection.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS stats (
                ts                TEXT    NOT NULL,
                conversation_id   INT,
                tokens_prompt     INT     NOT NULL,
                tokens_candidates INT     NOT NULL,
                tokens_total      INT     NOT NULL
            );
            """)

    def add(self, record: Record):
        with sqlite3.connect(self._db_name) as connection:
            cur = connection.cursor()
            cur.execute(
                """
                INSERT INTO stats
                VALUES (:ts, :conversation_id, :tokens_prompt, :tokens_candidates, :tokens_total)
                """,
                record.model_dump(),
            )
            connection.commit()

    def tokens_last_24h(self) -> int:
        with sqlite3.connect(self._db_name) as connection:
            cur = connection.cursor()
            cur.execute("SELECT SUM(tokens_total) FROM stats WHERE ts >= datetime('now', '-1 days')")
            result = cur.fetchone()
            return result[0] or 0

    def requests_last_24h(self) -> int:
        with sqlite3.connect(self._db_name) as connection:
            cur = connection.cursor()
            cur.execute("SELECT COUNT(*) FROM stats WHERE ts >= datetime('now', '-1 days')")
            result = cur.fetchone()
            return result[0] or 0

    def requests_last_minute(self) -> int:
        with sqlite3.connect(self._db_name) as connection:
            cur = connection.cursor()
            cur.execute("SELECT COUNT(*) FROM stats WHERE ts >= datetime('now', '-1 minutes')")
            result = cur.fetchone()
            return result[0] or 0


_db = Database(config.STATS_DB_NAME)


def add(response_usage: types.GenerateContentResponseUsageMetadata | None):
    if response_usage is None:
        return

    record = Record(
        # TODO implement
        conversation_id=None,
        tokens_prompt=response_usage.prompt_token_count or 0,
        tokens_candidates=response_usage.candidates_token_count or 0,
        tokens_total=response_usage.total_token_count or 0,
    )

    _db.add(record)


def print_usage():
    tok_24h = _db.tokens_last_24h()
    req_24h = _db.requests_last_24h()
    req_60s = _db.requests_last_minute()

    def percent(current, total) -> str:
        value = 100 * current / total
        rounded_one_digit = round(value, 1)
        # Add spaces at the start do that the percent symbols are aligned
        return f"{rounded_one_digit}%".rjust(5)

    print("Usage stats:")
    print(f"Tokens 24h:      {percent(tok_24h, config.STATS_MAX_TOKENS_PER_DAY)}    {tok_24h} / {config.STATS_MAX_TOKENS_PER_DAY}")
    print(f"Requests 24h:    {percent(req_24h, config.STATS_MAX_REQUESTS_PER_DAY)}    {req_24h} / {config.STATS_MAX_REQUESTS_PER_DAY}")
    print(f"Requests 60s:    {percent(req_60s, config.STATS_MAX_REQUESTS_PER_MINUTE)}    {req_60s} / {config.STATS_MAX_REQUESTS_PER_MINUTE}")
