import logging
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.utils.clickhouse import CLICKHOUSE_TABLE, get_clickhouse_client
from src.utils.jobs_schema import validate_and_cast_jobs_schema


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def get_latest_processed_file() -> Path:
    processed_files = sorted(Path("data/processed").glob("jobs_normalized_*.csv"))

    if not processed_files:
        raise FileNotFoundError("No processed files found in data/processed")

    return processed_files[-1]


def prepare_jobs_for_loading(df: pd.DataFrame) -> pd.DataFrame:
    prepared_df = df.copy()

    prepared_df["loaded_at"] = datetime.now(timezone.utc)

    prepared_df = validate_and_cast_jobs_schema(prepared_df)

    logger.info("Prepared %d jobs for ClickHouse loading",len(prepared_df))

    return prepared_df


def load_jobs_from_csv(file_path: Path) -> pd.DataFrame:
    logger.info("Loading jobs from %s", file_path)

    df = pd.read_csv(file_path)

    return prepare_jobs_for_loading(df)


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


def run_loader(df: pd.DataFrame | None = None) -> None:
    if df is None:
        latest_file = get_latest_processed_file()
        prepared_df = load_jobs_from_csv(latest_file)
    else:
        logger.info("Loading jobs directly from DataFrame")

        prepared_df = prepare_jobs_for_loading(df)

    insert_jobs(prepared_df)

    logger.info("ClickHouse loading finished successfully")


def main() -> None:
    run_loader()


if __name__ == "__main__":
    main()

















