import pytest
import tempfile
from datetime import datetime, timezone, timedelta
from stats import Database, Record, datetime_to_string, _now_utc


@pytest.fixture
def test_db():
    # File is automatically deleted on context manager exit
    with tempfile.NamedTemporaryFile() as file:
        yield Database(file.name)


def test_empty_db_returns_zero(test_db: Database):
    assert test_db.tokens_last_24h() == 0
    assert test_db.requests_last_24h() == 0
    assert test_db.requests_last_minute() == 0


def test_one_record(test_db: Database):
    test_db.add(Record(
        tokens_prompt=50,
        tokens_candidates=100,
        tokens_total=150,
    ))
    assert test_db.tokens_last_24h() == 150
    assert test_db.requests_last_24h() == 1
    assert test_db.requests_last_minute() == 1


def test_many_records(test_db: Database):
    for _ in range(5):
        test_db.add(Record(
            tokens_prompt=50,
            tokens_candidates=100,
            tokens_total=150,
        ))
    assert test_db.tokens_last_24h() == 150 * 5
    assert test_db.requests_last_24h() == 5
    assert test_db.requests_last_minute() == 5


def test_last_minute_boundary(test_db: Database):
    # More than a minute ago
    test_db.add(Record(
        ts=datetime_to_string(datetime.now(timezone.utc) - timedelta(seconds=62)),
        tokens_prompt=10,
        tokens_candidates=20,
        tokens_total=30,
    ))
    # Less than a minute ago
    test_db.add(Record(
        ts=datetime_to_string(datetime.now(timezone.utc) - timedelta(seconds=58)),
        tokens_prompt=40,
        tokens_candidates=50,
        tokens_total=90,
    ))
    assert test_db.tokens_last_24h() == 90 + 30
    assert test_db.requests_last_24h() == 2
    assert test_db.requests_last_minute() == 1


def test_last_24_hours_boundary(test_db: Database):
    # Requests older than 24 hours, should be ignored in "last_24h" counts
    for i in reversed(range(5)):
        test_db.add(Record(
            ts=datetime_to_string(datetime.now(timezone.utc) - timedelta(hours=24, minutes=2 ** i)),
            tokens_prompt=22,
            tokens_candidates=55,
            tokens_total=77,
        ))
    # Requests within 24 hours ago, should be considered
    test_db.add(Record(
        ts=datetime_to_string(datetime.now(timezone.utc) - timedelta(hours=23, minutes=59)),
        tokens_prompt=111,
        tokens_candidates=222,
        tokens_total=333,
    ))
    assert test_db.tokens_last_24h() == 333
    assert test_db.requests_last_24h() == 1
    assert test_db.requests_last_minute() == 0


class TestDatetimeFormatting:
    def test_datetime_to_string(self):
        assert datetime_to_string(datetime(2025, 5, 17, 11, 39))                      == "2025-05-17 11:39:00.000000"
        assert datetime_to_string(datetime(2025, 5, 17, 11, 39, tzinfo=timezone.utc)) == "2025-05-17 11:39:00.000000"
        # Epoch
        assert datetime_to_string(datetime(1970, 1, 1))                       == "1970-01-01 00:00:00.000000"
        assert datetime_to_string(datetime.fromtimestamp(0, tz=timezone.utc)) == "1970-01-01 00:00:00.000000"

    def test_now_conversion(self):
        now_utc = datetime.now(timezone.utc)
        # All string should match, excluding the subseconds part
        # This test can easily be flaky due to datetime.now() returning two different timestamps
        assert _now_utc()[:19] == datetime_to_string(now_utc)[:19]
