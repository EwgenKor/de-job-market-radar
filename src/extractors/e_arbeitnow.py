
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from src.utils.quality import run_quality_checks, filter_required_fields
from src.utils.s3 import upload_file_to_s3
from src.normalizers.n_arbeitnow import normalize_arbeitnow_jobs
from src.normalizers.common import build_batch_id

import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


load_dotenv()

API_URL = os.getenv("ARBEITNOW_API_URL")

SOURCE_NAME = "arbeitnow"

if not API_URL:
    raise ValueError("ARBEITNOW_API_URL is not set")


def fetch_jobs() -> dict:
    logger.info("Fetching jobs from %s", API_URL)

    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()

    data = response.json()

    return data


def save_raw_json(data: dict) -> Path:
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"jobs_raw_{datetime.now().date()}.json"
    file_path = output_dir / file_name

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info("Saved raw data to %s", file_path)

    return file_path


def save_processed_csv(df: pd.DataFrame) -> Path:
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"jobs_normalized_{datetime.now().date()}.csv"
    file_path = output_dir / file_name

    df.to_csv(file_path, index=False, encoding="utf-8")

    logger.info("Saved processed data to %s", file_path)

    return file_path


def run_extractor() -> pd.DataFrame:
    extracted_at = datetime.now(timezone.utc)
    run_date = extracted_at.date()

    batch_id = build_batch_id(
        source=SOURCE_NAME,
        run_datetime=extracted_at,
    )

    data = fetch_jobs()

    raw_file_path = save_raw_json(data)

    upload_file_to_s3(
        raw_file_path,
        f"raw/source={SOURCE_NAME}/dt={run_date}/{raw_file_path.name}",
    )

    df = normalize_arbeitnow_jobs(
        data=data,
        batch_id=batch_id,
        extracted_at=extracted_at,
    )

    run_quality_checks(df)
    df = filter_required_fields(df)

    logger.debug(
        "Sample normalized jobs:\n%s",
        df[
            [
                "title",
                "company",
                "location_raw",
                "country",
                "remote",
                "tags",
                "skills",
            ]
        ].head(),
    )

    logger.info("Normalized jobs DataFrame shape: %s", df.shape)

    processed_file_path = save_processed_csv(df)

    upload_file_to_s3(
        processed_file_path,
        f"processed/source={SOURCE_NAME}/dt={run_date}/{processed_file_path.name}",
    )

    logger.info("Arbeitnow extraction and normalization finished successfully")

    return df


def main() -> None:
    run_extractor()


if __name__ == "__main__":
    main()