
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from src.utils.quality import run_quality_checks, filter_required_fields
from src.utils.s3 import upload_file_to_s3

import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


load_dotenv()

API_URL = os.getenv("ARBEITNOW_API_URL")

if not API_URL:
    raise ValueError("ARBEITNOW_API_URL is not set")


SKILL_KEYWORDS = {
    "python": ["python", "python3"],
    "sql": ["sql"],
    "postgres": ["postgres", "postgresql"],
    "mysql": ["mysql"],
    "mongodb": ["mongodb", "mongo"],
    "redis": ["redis"],

    "airflow": ["airflow", "apache airflow"],
    "dbt": ["dbt"],
    "spark": ["spark", "apache spark", "pyspark"],
    "kafka": ["kafka", "apache kafka"],
    "flink": ["flink", "apache flink"],

    "aws": ["aws", "amazon web services"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "azure": ["azure"],

    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "terraform": ["terraform"],

    "clickhouse": ["clickhouse"],
    "snowflake": ["snowflake"],
    "bigquery": ["bigquery", "google bigquery"],
    "redshift": ["redshift", "amazon redshift"],
    "databricks": ["databricks"],

    "linux": ["linux"],
    "bash": ["bash", "shell scripting"],
    "git": ["git", "github", "gitlab"],

    "pandas": ["pandas"],
    "numpy": ["numpy"],

    "etl": ["etl", "elt"],
    "data warehouse": ["data warehouse", "dwh"],
    "data lake": ["data lake", "lakehouse"],
    "api": ["api", "rest api", "restful"],
}


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

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info("Saved raw data to %s", file_path)

    return file_path


def safe_get(value, default=None):
    if value is None:
        return default

    if isinstance(value, str):
        value = value.strip()
        return value if value else default

    return value


def normalize_tags(tags) -> list[str]:
    if not isinstance(tags, list):
        return []

    clean_tags = []

    for tag in tags:
        clean_tag = safe_get(tag)

        if clean_tag is not None:
            clean_tags.append(clean_tag)

    return clean_tags


def extract_skills(title, tags, description=None) -> list[str]:
    text_parts = []

    if title:
        text_parts.append(title)

    if description:
        text_parts.append(description)

    if tags:
        text_parts.extend(tags)

    text = " ".join(text_parts).lower()

    found_skills = set()

    for skill, keywords in SKILL_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                found_skills.add(skill)
                break

    return sorted(found_skills)


def normalize_jobs(data: dict) -> pd.DataFrame:
    jobs = data.get("data", [])

    normalize_jobs = []

    for job in jobs:
        title = safe_get(job.get("title"))
        company = safe_get(job.get("company_name"))
        location = safe_get(job.get("location"))
        remote = job.get("remote")
        url = safe_get(job.get("url"))
        tags = normalize_tags(job.get("tags"))
        created_at = safe_get(job.get("created_at"))
        description = safe_get(job.get("description"))

        normalize_jobs.append(
            {
                "source": "arbeitnow",
                "title": title,
                "company": company,
                "location": location,
                "remote": remote,
                "url": url,
                "tags": tags,
                "skills": extract_skills(title, tags, description),
                "created_at": created_at,
                "description": description,
            }
        )
    df = pd.DataFrame(normalize_jobs)

    return df


def save_processed_csv(df: pd.DataFrame) -> Path:
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"jobs_normalized_{datetime.now().date()}.csv"
    file_path = output_dir / file_name

    df.to_csv(file_path, index=False, encoding="utf-8")

    logger.info("Saved processed data to %s", file_path)

    return file_path


def main() -> None:
    data = fetch_jobs()

    raw_file_path = save_raw_json(data)

    upload_file_to_s3(
        raw_file_path,
        f"raw/{raw_file_path.name}",
    )

    df = normalize_jobs(data)

    run_quality_checks(df)
    df = filter_required_fields(df)

    logger.debug(
        "Sample normalized jobs:\n%s",
        df[
            [
                "title",
                "company",
                "location",
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
        f"processed/{processed_file_path.name}",
    )

    logger.info("Pipeline finished successfully")


if __name__ == "__main__":
    main()