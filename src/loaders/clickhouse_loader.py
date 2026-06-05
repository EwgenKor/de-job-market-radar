import ast
import logging
import os
from pathlib import Path

import clickhouse_connect
import pandas as pd
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)

load_dotenv()

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DATABASE", "job_radar")
CLICKHOUSE_TABLE = os.getenv("CLICKHOUSE_TABLE", "jobs")


def get_latest_processed_file() -> Path:
    processed_files = sorted(Path("data/processed").glob("jobs_normalized_*.csv"))

    if not processed_files:
        raise FileNotFoundError("No processed files found in data/processed")

    return processed_files[-1]


def parse_list_columns(value) -> list[str]:
    if isinstance(value, list):
        return value

    if pd.isna(value):
        return []

    if isinstance(value, str):
        try:
            parsed = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            logger.warning("Failed to parse %s", value)
            return []

        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]

    return []


def load_jobs_from_csv(file_path: Path) -> pd.DataFrame:
    logger.info("Loading jobs from %s", file_path)

    df = pd.read_csv(file_path)

    df["tags"] = df["tags"].apply(parse_list_columns)
    df["skills"] = df["skills"].apply(parse_list_columns)

    string_columns = [
        "source",
        "title",
        "company",
        "location",
        "url",
        "created_at",
        "description",
    ]

    for column in string_columns:
        df[column] = df[column].astype("string")

    df = df[
        [
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
        ]
    ]

    logger.info("Loaded %d jobs from CSV", len(df))

    return df


def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        database=CLICKHOUSE_DB,
    )


def insert_jobs(df: pd.DataFrame) -> None:
    client = get_clickhouse_client()

    client.insert_df(
        table=CLICKHOUSE_TABLE,
        df=df,
    )

    logger.info(
        "Inserted %d rows in %s.%s",
        len(df),
        CLICKHOUSE_DB,
        CLICKHOUSE_TABLE,
    )


def main():
    latest_file = get_latest_processed_file()
    df = load_jobs_from_csv(latest_file)

    insert_jobs(df)

    logger.info("Clickhouse loading finished successfully")


if __name__ == "__main__":
    main()

















