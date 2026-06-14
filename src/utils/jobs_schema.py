import ast
import logging

import pandas as pd


logger = logging.getLogger(__name__)


REQUIRED_COLUMNS = [
    "source",
    "title",
    "company",
    "location",
    "remote",
    "url",
    "tags",
    "skills",
    "created_at",
    "description",
    "loaded_at",
]


STRING_COLUMNS = [
    "source",
    "title",
    "company",
    "location",
    "url",
    "created_at",
    "description",
]


LIST_COLUMNS = [
    "tags",
    "skills",
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


def validate_and_cast_jobs_schema(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    for column in LIST_COLUMNS:
        df[column] = df[column].apply(parse_list_column)

    for column in STRING_COLUMNS:
        df[column] = df[column].astype("string")

    df["loaded_at"] = pd.to_datetime(df["loaded_at"])

    logger.info("Jobs schema validation passed")

    return df[REQUIRED_COLUMNS]