
import json
import os
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv
from src.utils.quality import run_quality_checks, filter_required_fields

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
    "python": ["python"],
    "sql": ["sql", "postgresql", "postgres", "mysql"],
    "airflow": ["airflow", "apache airflow"],
    "spark": ["spark", "apache spark", "pyspark"],
    "kafka": ["kafka", "apache kafka"],
    "dbt": ["dbt"],
    "aws": ["aws", "amazon web services"],
    "gcp": ["gcp", "google cloud"],
    "azure": ["azure"],
    "docker": ["docker"],
    "kubernetes": ["kubernetes", "k8s"],
    "clickhouse": ["clickhouse"],
    "postgres": ["postgres", "postgresql"],
}


def fetch_jobs():
    response = requests.get(API_URL, timeout=30)
    response.raise_for_status()
    data = response.json()
    return data


def save_raw_json(data: dict):
    output_dir = Path("data/raw")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"jobs_raw_{datetime.now().date()}.json"
    file_path = output_dir / file_name

    with open(file_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info("Saved raw data to %s", file_path)


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

    found_skills = []

    for skill, keywords in SKILL_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                found_skills.append(skill)
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


def save_processed_csv(df: pd.DataFrame) -> None:
    output_dir = Path("data/processed")
    output_dir.mkdir(parents=True, exist_ok=True)

    file_name = f"jobs_normalized_{datetime.now().date()}.csv"
    file_path = output_dir / file_name

    df.to_csv(file_path, index=False, encoding="utf-8")

    logger.info("Saved processed data to %s", file_path)


def main():
    data = fetch_jobs()
    save_raw_json(data)

    df = normalize_jobs(data)

    run_quality_checks(df)
    df = filter_required_fields(df)

    save_processed_csv(df)

    logger.debug("Sample normalized jobs:\n%s", df[["title", "company", "location", "remote", "tags", "skills"]].head())
    logger.info("Normalized jobs DataFrame shape: %s", df.shape)


if __name__ == "__main__":
    main()