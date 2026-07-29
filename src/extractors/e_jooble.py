import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

from src.normalizers.common import build_batch_id
from src.normalizers.n_jooble import normalize_jooble_jobs
from src.utils.quality import filter_required_fields, run_quality_checks
from src.utils.s3 import upload_file_to_s3


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


load_dotenv()


SOURCE_NAME = "jooble"

API_KEY = os.getenv("JOOBLE_API_KEY")
SEARCH_KEYWORDS = os.getenv(
    "JOOBLE_SEARCH_KEYWORDS",
    "Data Engineer",
)
SEARCH_LOCATION = os.getenv(
    "JOOBLE_SEARCH_LOCATION",
    "Germany",
)
RESULTS_PER_PAGE = int(os.getenv(
    "JOOBLE_RESULTS_PER_PAGE",
    "100"
)
)


if not API_KEY:
    raise ValueError(
        "JOOBLE_API_KEY is not set"
    )


API_URL = f"https://jooble.org/api/{API_KEY}"


def fetch_jobs() -> dict:
    logger.info(
        "Fetching Jooble jobs: keywords=%s, location=%s",
        SEARCH_KEYWORDS,
        SEARCH_LOCATION,
    )

    payload = {
        "keywords": SEARCH_KEYWORDS,
        "location": SEARCH_LOCATION,
        "page": "1",
        "ResultOnPage": RESULTS_PER_PAGE,
        "companysearch": "false",
    }

    response = requests.post(
        API_URL,
        json=payload,
        timeout=30,
        headers={"Content-Type": "application/json", "User-Agent": "JobRadar/1.0"},
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, dict):
        raise ValueError("Unexpected Jooble response: expected a dictionary")

    if "jobs" not in data:
        raise ValueError("Unexpected Jooble response: missing 'jobs' field")

    if not isinstance(data["jobs"], list):
        raise ValueError("Unexpected Jooble response: 'jobs' must be a list")

    logger.info(
        "Jooble returned %d jobs; total available: %s",
        len(data["jobs"]),
        data.get("totalCount"),
    )

    return data


def save_raw_json(data: dict, run_date) -> Path:
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"jobs_raw_{SOURCE_NAME}_{run_date}.json"
    file_path = output_dir / file_name

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

    logger.info("Saved raw data to %s", file_path)

    return file_path


def save_processed_csv(df: pd.DataFrame, run_date) -> Path:
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = (f"jobs_normalized_{SOURCE_NAME}_{run_date}.csv")
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

    raw_file_path = save_raw_json(
        data=data,
        run_date=run_date,
    )

    upload_file_to_s3(
        raw_file_path,
        f"raw/source={SOURCE_NAME}/dt={run_date}/{raw_file_path.name}",
    )

    df = normalize_jooble_jobs(
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

    processed_file_path = save_processed_csv(
        df=df,
        run_date=run_date,
    )

    upload_file_to_s3(
        processed_file_path,
        (
            f"processed/source={SOURCE_NAME}/"
            f"dt={run_date}/"
            f"{processed_file_path.name}"
        ),
    )

    logger.info("Jooble extraction and normalization finished successfully")

    return df


def main() -> None:
    run_extractor()


if __name__ == "__main__":
    main()