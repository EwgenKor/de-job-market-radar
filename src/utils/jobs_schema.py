import ast
import logging

import pandas as pd


logger = logging.getLogger(__name__)


REQUIRED_COLUMNS = [
    "batch_id",
    "source",
    "source_job_id",
    "title",
    "company",
    "location_raw",
    "country",
    "remote",
    "url",
    "tags",
    "skills",
    "created_at",
    "extracted_at",
    "description",
    "loaded_at",
]


STRING_COLUMNS = [
    "batch_id",
    "source",
    "source_job_id",
    "title",
    "company",
    "location_raw",
    "country",
    "url",
    "created_at",
    "description",
]


DATETIME_COLUMNS = [
    "extracted_at",
    "loaded_at",
]


LIST_COLUMNS = [
    "tags",
    "skills",
]


CRITICAL_NON_EMPTY_COLUMNS = [
    "batch_id",
    "source",
    "source_job_id",
    "title",
    "url",
]


def parse_list_column(value) -> list[str]:
    if isinstance(value, list):
        return value

    if not isinstance(value, str):
        return []

    try:
        parsed = ast.literal_eval(value)
    except (ValueError, SyntaxError):
        return []

    return parsed if isinstance(parsed, list) else []


def validate_required_columns(df: pd.DataFrame) -> None:
    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )


def cast_list_columns(df: pd.DataFrame) -> None:
    for column in LIST_COLUMNS:
        df[column] = df[column].apply(parse_list_column)


def cast_string_columns(df: pd.DataFrame) -> None:
    for column in STRING_COLUMNS:
        df[column] = (
            df[column]
            .fillna("")
            .astype("string")
        )


def cast_datetime_columns(df: pd.DataFrame) -> None:
    for column in DATETIME_COLUMNS:
        df[column] = pd.to_datetime(
            df[column],
            errors="coerce",
        )


def cast_remote_column(df: pd.DataFrame) -> None:
    df["remote"] = df["remote"].fillna(False).astype(bool)


def validate_non_empty_columns(df: pd.DataFrame) -> None:
    empty_values = {}

    for column in CRITICAL_NON_EMPTY_COLUMNS:
        empty_count = int(
            df[column]
            .str.strip()
            .eq("")
            .sum()
        )

        if empty_count > 0:
            empty_values[column] = empty_count

    if empty_values:
        raise ValueError(
            f"Empty required values found: {empty_values}"
        )


def validate_datetime_columns(df: pd.DataFrame) -> None:
    invalid_datetimes = {}

    for column in DATETIME_COLUMNS:
        invalid_count = int(df[column].isna().sum())

        if invalid_count > 0:
            invalid_datetimes[column] = invalid_count

    if invalid_datetimes:
        raise ValueError(
            f"Invalid datetime values found: {invalid_datetimes}"
        )


def validate_and_cast_jobs_schema(
    df: pd.DataFrame,
) -> pd.DataFrame:
    df = df.copy()

    validate_required_columns(df)

    cast_list_columns(df)
    cast_string_columns(df)
    cast_datetime_columns(df)
    cast_remote_column(df)

    validate_non_empty_columns(df)
    validate_datetime_columns(df)

    logger.info(
        "Jobs schema validation passed for %d rows",
        len(df),
    )

    return df[REQUIRED_COLUMNS]