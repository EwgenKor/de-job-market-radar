import pandas as pd

from src.normalizers.common import (
    generate_source_job_id,
    normalize_country,
    normalize_url,
)


SOURCE_NAME = "remoteok"


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


def normalize_remoteok_jobs(
    data: list[dict],
    batch_id: str,
    extracted_at,
) -> pd.DataFrame:

    jobs = [job for job in data if isinstance(job, dict) and "id" in job]

    normalized_jobs = []

    for job in jobs:
        title = safe_get(job.get("position"))
        company = safe_get(job.get("company"))
        location_raw = safe_get(job.get("location"))
        remote = True
        raw_url = safe_get(job.get("url"))
        url = normalize_url(raw_url)
        tags = normalize_tags(job.get("tags"))
        created_at = safe_get(job.get("date"))
        description = safe_get(job.get("description"))

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
                "remote": remote,
                "url": url,
                "tags": tags,
                "skills": extract_skills(
                    title,
                    tags,
                    description,
                ),
                "created_at": created_at,
                "extracted_at": extracted_at,
                "description": description,
            }
        )

    return pd.DataFrame(normalized_jobs)

