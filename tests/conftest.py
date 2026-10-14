import pytest

from vorsa.db.connection import connect
from vorsa.db.migrate import apply_migrations


@pytest.fixture
def db():
    """Database kosong di memori dengan skema terbaru."""
    conn = connect(":memory:")
    apply_migrations(conn)
    yield conn
    conn.close()
