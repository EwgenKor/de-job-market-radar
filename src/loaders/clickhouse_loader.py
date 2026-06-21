import logging
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.utils.clickhouse import CLICKHOUSE_TABLE, get_clickhouse_client
from src.utils.jobs_schema import validate_and_cast_jobs_schema


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)

logger = logging.getLogger(__name__)


def get_latest_processed_file() -> Path:
    processed_files = sorted(Path("data/processed").glob("jobs_normalized_*.csv"))

    if not processed_files:
        raise FileNotFoundError("No processed files found in data/processed")

    return processed_files[-1]


def load_jobs_from_csv(file_path: Path) -> pd.DataFrame:
    logger.info("Loading jobs from %s", file_path)

    df = pd.read_csv(file_path)

    df["loaded_at"] = datetime.now()

    df = validate_and_cast_jobs_schema(df)

    logger.info("Loaded %d jobs from CSV", len(df))

    return df


def insert_jobs(df: pd.DataFrame) -> None:
    client = get_clickhouse_client()

    client.insert_df(
        table=CLICKHOUSE_TABLE,
        df=df,
    )

    logger.info(
        "Inserted %d rows into ClickHouse",
        len(df),
    )


def run_loader() -> None:
    latest_file = get_latest_processed_file()
    df = load_jobs_from_csv(latest_file)

    insert_jobs(df)

    logger.info("ClickHouse loading finished successfully")


def main() -> None:
    run_loader()


if __name__ == "__main__":
    main()

















