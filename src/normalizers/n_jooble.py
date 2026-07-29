import pandas as pd

from src.normalizers.common import (
    generate_source_job_id,
    normalize_country,
    normalize_url,
)


SOURCE_NAME = "jooble"


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


REMOTE_KEYWORDS = {
    "remote",
    "fully remote",
    "work from home",
    "home office",
    "anywhere",
}


def safe_get(value, default=None):
    if value is None:
        return default

    if isinstance(value, str):
        value = value.strip()
        return value if value else default

    return value


def extract_skills(title, tags, description=None,) -> list[str]:
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


def detect_remote(title, location, description,) -> bool:
    text = " ".join(
        value
        for value in [
            title,
            location,
            description,
        ]
        if isinstance(value, str)
    ).lower()

    return any(keyword in text for keyword in REMOTE_KEYWORDS)


def normalize_jooble_jobs(
    data: dict,
    batch_id: str,
    extracted_at,
) -> pd.DataFrame:
    jobs = data.get("jobs", [])

    normalized_jobs = []

    for job in jobs:
        if not isinstance(job, dict):
            continue

        title = safe_get(job.get("title"))
        company = safe_get(job.get("company"))
        location_raw = safe_get(job.get("location"))
        description = safe_get(job.get("snippet"))
        raw_url = safe_get(job.get("link"))
        url = normalize_url(raw_url)
        created_at = safe_get(job.get("updated"))

        job_type = safe_get(job.get("type"))
        salary = safe_get(job.get("salary"))

        tags = [value for value in [job_type, salary] if value is not None]

        source_job_id = generate_source_job_id(
            source=SOURCE_NAME,
            source_job_id=job.get("id"),
            url=url,
        )

        normalized_jobs.append(
            {
                "batch_id": batch_id,
                "source": SOURCE_NAME,
                "source_job_id": source_job_id,
                "title": title,
                "company": company,
                "location_raw": location_raw,
                "country": normalize_country(location_raw),
                "remote": detect_remote(
                    title=title,
                    location=location_raw,
                    description=description,
                ),
                "url": url,
                "tags": tags,
                "skills": extract_skills(
                    title=title,
                    tags=tags,
                    description=description,
                ),
                "created_at": created_at,
                "extracted_at": extracted_at,
                "description": description,
            }
        )

    return pd.DataFrame(normalized_jobs)