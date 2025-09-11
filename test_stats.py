import pytest
import tempfile
from stats import Database


@pytest.fixture
def test_db():
    # File is automatically deleted on context manager exit
    with tempfile.NamedTemporaryFile() as file:
        yield Database(file.name)


def test_empty_db_returns_zero(test_db: Database):
    assert test_db.tokens_last_24h() == 0
    assert test_db.requests_last_24h() == 0
    assert test_db.requests_last_minute() == 0
