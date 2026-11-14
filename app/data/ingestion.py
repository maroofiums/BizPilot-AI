
import re
import sqlite3

from dataclasses import dataclass
from pathlib import Path

from app.core.logging import get_logger
from app.data.database import get_connection
from app.data.validation import validate_csv


logger = get_logger(__name__)


class DatasetIngestionError(RuntimeError):
    """Raised when a validated dataset cannot be stored."""


@dataclass(frozen=True)
class IngestionResult:
    """Metadata returned after successful dataset ingestion."""

    table_name: str
    row_count: int
    columns: list[str]


def generate_table_name(filename: str) -> str:
    """Generate a safe SQLite table name from a filename."""

    stem = Path(filename).stem.lower()

    safe_name = re.sub(
        r"[^a-zA-Z0-9_]+",
        "_",
        stem,
    ).strip("_")

    safe_name = safe_name[:50] or "upload"

    return f"dataset_{safe_name}"


def ingest_csv(
    filename: str,
    file_content: bytes,
    database_path: Path | None = None,
) -> IngestionResult:
    """
    Validate a CSV file and store its records in SQLite.
    """

    df = validate_csv(filename, file_content)

    table_name = generate_table_name(filename)

    try:
        with get_connection(database_path) as connection:

            # Prevent accidental replacement of existing datasets.
            existing_table = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name = ?
                """,
                (table_name,),
            ).fetchone()

            if existing_table:
                raise DatasetIngestionError(
                    f"Dataset table '{table_name}' already exists."
                )

            df.to_sql(
                name=table_name,
                con=connection,
                if_exists="fail",
                index=False,
            )

        logger.info(
            "Dataset ingested: table=%s rows=%d columns=%d",
            table_name,
            len(df),
            len(df.columns),
        )

        return IngestionResult(
            table_name=table_name,
            row_count=len(df),
            columns=df.columns.tolist(),
        )

    except DatasetIngestionError:
        raise

    except Exception as exc:
        logger.exception(
            "Dataset ingestion failed for table=%s",
            table_name,
        )

        raise DatasetIngestionError(
            "Failed to store the uploaded dataset."
        ) from exc
