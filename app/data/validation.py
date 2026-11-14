
from io import BytesIO
from pathlib import Path

import pandas as pd

from app.core.config import settings


MAX_ROWS = 100_000
MAX_COLUMNS = 100


class DatasetValidationError(ValueError):
      """Raised when an uploaded dataset fails validation."""


def validate_file_extension(filename: str) -> None:
    """Ensure the uploaded file is a CSV."""

    if Path(filename).suffix.lower() != ".csv":
        raise DatasetValidationError(
            "Only CSV files are supported."
        )


def validate_file_size(file_content: bytes) -> None:
    """Ensure the uploaded file does not exceed the size limit."""

    if not file_content:
        raise DatasetValidationError("Uploaded file is empty.")

    max_size = settings.max_upload_size_mb * 1024 * 1024

    if len(file_content) > max_size:
        raise DatasetValidationError(
            f"File exceeds the {settings.max_upload_size_mb} MB limit."
        )


def validate_dataframe(df: pd.DataFrame) -> None:
    """Validate the structure and contents of a dataset."""

    if df.empty:
        raise DatasetValidationError(
            "Dataset contains no records."
        )

    if len(df) > MAX_ROWS:
        raise DatasetValidationError(
            f"Dataset exceeds the {MAX_ROWS} row limit."
        )

    if len(df.columns) > MAX_COLUMNS:
        raise DatasetValidationError(
            f"Dataset exceeds the {MAX_COLUMNS} column limit."
        )

    if not df.columns.is_unique:
        raise DatasetValidationError(
            "Dataset contains duplicate column names."
        )

    if any(
        not isinstance(column, str) or not column.strip()
        for column in df.columns
    ):
        raise DatasetValidationError(
            "Column names must be non-empty strings."
        )

    if df.isna().all().any():
        raise DatasetValidationError(
            "Dataset contains completely empty columns."
        )


def validate_csv(
    filename: str,
    file_content: bytes,
) -> pd.DataFrame:
    """
    Validate a CSV upload and return its parsed DataFrame.
    """

    validate_file_extension(filename)
    validate_file_size(file_content)

    try:
        df = pd.read_csv(
            BytesIO(file_content),
            encoding="utf-8-sig",
            on_bad_lines="error",
        )

    except (pd.errors.ParserError, UnicodeDecodeError) as exc:
        raise DatasetValidationError(
            "Unable to parse CSV. Check its encoding and structure."
        ) from exc

    except pd.errors.EmptyDataError as exc:
        raise DatasetValidationError(
            "CSV file contains no data."
        ) from exc

    validate_dataframe(df)

    return df
