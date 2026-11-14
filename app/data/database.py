
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.core.config import settings


def _connect(database_path: Path) -> sqlite3.Connection:
    """Create and configure a SQLite connection."""

    connection = sqlite3.connect(
        database_path,
        timeout=30,
    )

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA busy_timeout = 30000")

    return connection


@contextmanager
def get_connection(
    database_path: Path | None = None,
) -> Iterator[sqlite3.Connection]:
    """
    Provide a database connection with automatic
    commit, rollback, and cleanup.
    """

    path = database_path or settings.database_path
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = _connect(path)

    try:
        yield connection
        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()


def initialize_database(
    database_path: Path | None = None,
) -> None:
    """Initialize the SQLite database."""

    path = database_path or settings.database_path
    path.parent.mkdir(parents=True, exist_ok=True)

    connection = _connect(path)

    try:
        connection.execute("PRAGMA journal_mode = WAL")
        connection.commit()

    finally:
        connection.close()
