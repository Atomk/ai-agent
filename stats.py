import sqlite3
import time
from datetime import datetime, timezone

from google.genai import types
from pydantic import BaseModel

import config


_DB_NAME = "api_stats.db"


class Record(BaseModel):
    conversation_id: int | None
    tokens_prompt: int
    tokens_candidates: int
    # Computed field, can delete column
    tokens_total: int


class Database:
    # TODO pass db name as argument so it's easier to test
    def __init__(self) -> None:
        with sqlite3.connect(_DB_NAME) as connection:
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
        with sqlite3.connect(_DB_NAME) as connection:
            cur = connection.cursor()
            cur.execute(
                """
                INSERT INTO stats
                VALUES (datetime('now','utc','subsec'), :conversation_id, :tokens_prompt, :tokens_candidates, :tokens_total)
                """,
                record.model_dump(),
            )
            connection.commit()

    def tokens_last_24h(self) -> int:
        with sqlite3.connect(_DB_NAME) as connection:
            cur = connection.cursor()
            cur.execute("SELECT SUM(tokens_total) FROM stats WHERE ts >= datetime('now', 'utc', '-1 days')")
            result = cur.fetchone()
            return result[0] or 0

    def requests_last_24h(self) -> int:
        with sqlite3.connect(_DB_NAME) as connection:
            cur = connection.cursor()
            cur.execute("SELECT COUNT(*) FROM stats WHERE ts >= datetime('now', 'utc', '-1 days')")
            result = cur.fetchone()
            return result[0] or 0

    def requests_last_minute(self) -> int:
        with sqlite3.connect(_DB_NAME) as connection:
            cur = connection.cursor()
            cur.execute("SELECT COUNT(*) FROM stats WHERE ts >= datetime('now', 'utc', '-1 minutes')")
            result = cur.fetchone()
            return result[0] or 0


_db = Database()


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
    print(f"Tokens:          {percent(tok_24h, config.STATS_MAX_TOKENS_PER_DAY)}    {tok_24h} / {config.STATS_MAX_TOKENS_PER_DAY}")
    print(f"Requests 24h:    {percent(req_24h, config.STATS_MAX_REQUESTS_PER_DAY)}    {req_24h} / {config.STATS_MAX_REQUESTS_PER_DAY}")
    print(f"Requests 60s:    {percent(req_60s, config.STATS_MAX_REQUESTS_PER_MINUTE)}    {req_60s} / {config.STATS_MAX_REQUESTS_PER_MINUTE}")
