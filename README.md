# Job RADAR

**Job RADAR** is a portfolio-ready Data Engineering project for collecting, processing, storing, and analyzing job market data.

The project implements a complete multi-source data pipeline:

```text
Job APIs
   ↓
Extraction
   ↓
Raw Storage
   ↓
Normalization
   ↓
Data Quality
   ↓
Multi-source Combination
   ↓
Deduplication
   ↓
ClickHouse
   ↓
Analytical Marts
   ↓
Apache Superset
```

The main focus of the project is Data Engineering: reliable ingestion, canonical data modeling, storage layers, orchestration, analytical marts, and reproducible processing.

---

## Dashboard

Job RADAR includes an Apache Superset dashboard built on top of ClickHouse analytical marts.

The dashboard currently provides:

- total vacancies;
- unique companies;
- detected technical skills;
- remote vacancies;
- job market trends;
- remote vs non-remote distribution;
- top companies;
- top job locations.

![Job RADAR Market Overview](docs/images/job_radar_market_overview.png)

---

## Current Release

**Job RADAR v1.0.0**

The first portfolio-ready version includes:

- 3 job data sources;
- raw and processed data layers;
- S3-compatible object storage;
- canonical job schema;
- data quality checks;
- multi-source batch combination;
- cross-source deduplication;
- ClickHouse analytical storage;
- 7 analytical marts;
- Airflow orchestration;
- Apache Superset dashboard.

---

# Data Sources

The current pipeline collects jobs from:

- **Arbeitnow**
- **RemoteOK**
- **Jooble**

Each source is implemented as an independent extractor module.

The extractor performs the complete source-specific workflow:

```text
API request
    ↓
Fail-fast response validation
    ↓
Save raw JSON
    ↓
Upload raw data to MinIO
    ↓
Build batch_id
    ↓
Normalize
    ↓
Quality checks
    ↓
Save processed CSV
    ↓
Upload processed data to MinIO
    ↓
Return pandas DataFrame
```

This keeps source-specific logic isolated while all sources produce the same canonical output schema.

---

# Architecture

```text
                ┌─────────────┐
                │ Arbeitnow   │
                └──────┬──────┘
                       │
                ┌─────────────┐
                │ RemoteOK    │
                └──────┬──────┘
                       │
                ┌─────────────┐
                │ Jooble      │
                └──────┬──────┘
                       │
                       ▼
              Source Extractors
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
         Raw JSON          Source Normalization
             │                   │
             ▼                   ▼
           MinIO           Quality Checks
                                 │
                                 ▼
                          Processed CSV
                                 │
                                 ▼
                               MinIO
                                 │
                                 ▼
                      Normalized DataFrames
                                 │
                                 ▼
                     Combine Normalized Batches
                                 │
                                 ▼
                          Deduplication
                                 │
                                 ▼
                            ClickHouse
                                 │
                                 ▼
                        Analytical Marts
                                 │
                                 ▼
                         Apache Superset
```

---

# Canonical Job Schema

All sources are normalized into the same schema:

```text
batch_id
source
source_job_id
title
company
location_raw
country
remote
url
tags
skills
created_at
extracted_at
description
```

The ClickHouse loader adds:

```text
loaded_at
```

The final ClickHouse schema therefore contains:

```text
batch_id
source
source_job_id
title
company
location_raw
country
remote
url
tags
skills
created_at
extracted_at
description
loaded_at
```

---

# Storage Layers

## Raw Layer

Original API responses are stored as JSON.

Local development:

```text
data/raw/
```

MinIO:

```text
raw/
└── source=<source>/
    └── dt=<YYYY-MM-DD>/
```

Raw data is preserved before normalization so source responses can be inspected or reprocessed later.

---

## Processed Layer

Normalized datasets are stored as CSV.

Local development:

```text
data/processed/
```

MinIO:

```text
processed/
└── source=<source>/
    └── dt=<YYYY-MM-DD>/
```

Processed files follow the canonical Job RADAR schema.

---

# Multi-source Processing

Each extractor returns a normalized pandas DataFrame.

The pipeline collects them into:

```python
normalized_batches = [
    run_arbeitnow(),
    run_remoteok(),
    run_jooble(),
]
```

The batches are combined before loading into ClickHouse.

```text
normalized DataFrames
        ↓
pd.concat()
        ↓
deduplication
        ↓
schema validation
        ↓
ClickHouse
```

The current deduplication layer handles exact duplicates using stable identifiers and normalized URLs.

More advanced fuzzy matching is intentionally outside the v1.0 scope.

---

# ClickHouse

ClickHouse is used as the analytical database.

Main database:

```text
job_radar
```

Main table:

```text
jobs
```

The table uses `ReplacingMergeTree` to support repeated pipeline loads while keeping the analytical model simple.

Before insertion, the loader:

1. accepts the combined DataFrame;
2. adds `loaded_at`;
3. validates the canonical schema;
4. converts list-like columns;
5. inserts the batch into ClickHouse.

The loader can also be executed manually against the latest processed CSV for debugging and recovery.

---

# Analytical Marts

Job RADAR v1.0 contains seven ClickHouse marts.

## `skills_mart`

Skill demand:

```text
skill
vacancies
remote_vacancies
non_remote_vacancies
unique_companies
```

## `remote_mart`

Remote vs non-remote market distribution:

```text
work_format
vacancies
unique_companies
```

## `companies_mart`

Company-level statistics:

```text
company
vacancies
remote_vacancies
non_remote_vacancies
unique_skills
```

## `locations_mart`

Location-level statistics:

```text
location_raw
vacancies
remote_vacancies
non_remote_vacancies
unique_companies
```

## `skill_pairs_mart`

Frequently occurring combinations of technical skills:

```text
skill_1
skill_2
vacancies
remote_vacancies
unique_companies
```

## `daily_snapshot_mart`

Daily job-market snapshots:

```text
snapshot_date
total_vacancies
remote_vacancies
non_remote_vacancies
unique_companies
unique_skills
```

## `daily_country_mart`

Daily country-level statistics:

```text
snapshot_date
country
vacancies
non_remote_vacancies
onsite_vacancies
unique_companies
```

---

# Airflow

Apache Airflow orchestrates the pipeline.

Executor:

```text
LocalExecutor
```

Airflow metadata database:

```text
PostgreSQL
```

Current DAG:

```text
job_radar_pipeline
```

The DAG runs the Job RADAR pipeline on schedule.

The application pipeline performs:

```text
Extract and normalize sources
        ↓
Combine normalized batches
        ↓
Deduplicate
        ↓
Load to ClickHouse
        ↓
Refresh analytical marts
```

Retries and active-run limits are configured at the DAG level.

---

# Dashboard

Apache Superset connects directly to the ClickHouse analytical layer.

Current dashboard:

```text
Job RADAR — Market Overview
```

Current visualizations include:

### KPI

- Total Vacancies
- Unique Companies
- Detected Skills
- Remote Vacancies

### Market Analytics

- Job Market Trend
- Remote vs Non-Remote
- Top Companies by Vacancies
- Top Job Locations

The dashboard deliberately reads analytical marts rather than rebuilding analytical logic directly from the raw `jobs` table.

---

---

# Tests

Focused unit tests cover core deterministic logic:

- URL normalization;
- tracking-parameter removal;
- deterministic fallback `source_job_id`;
- country normalization;
- `batch_id` generation;
- multi-source DataFrame combination;
- empty-batch handling;
- exact source-level deduplication;
- exact cross-source URL deduplication.

Run:

```bash
uv run pytest -q
```

Current result:

```text
11 passed
```

The test suite intentionally focuses on pure core logic first; broader integration testing is a post-v1 improvement.


# Tech Stack

## Data Engineering

- Python 3.12
- pandas
- requests
- python-dotenv
- boto3
- clickhouse-connect

## Infrastructure

- Docker
- Docker Compose

## Object Storage

- MinIO
- S3-compatible storage layout

## Analytical Database

- ClickHouse

## Orchestration

- Apache Airflow 2.9.3
- LocalExecutor
- PostgreSQL

## Analytics / BI

- Apache Superset

## Testing

- pytest

## Development

- uv
- Git
- GitHub

---

# Project Structure

```text
de_job_radar/
│
├── airflow/
│   ├── dags/
│   │   └── job_radar_pipeline_dag.py
│   ├── config/
│   ├── logs/
│   └── plugins/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
│
├── docs/
│   ├── architecture.md
│   ├── roadmap.md
│   ├── PORTFOLIO.md
│   ├── images/
│   │   └── job_radar_market_overview.png
│   └── checkpoints/
│       └── 2026-08-02_v1.0.0_release.md
│
├── sql/
│   ├── basic_analysis.sql
│   └── clickhouse/
│       ├── create_tables/
│       └── refresh_marts/
│
├── src/
│   ├── extractors/
│   │   ├── e_arbeitnow.py
│   │   ├── e_remoteok.py
│   │   └── e_jooble.py
│   │
│   ├── normalizers/
│   │   ├── common.py
│   │   ├── n_arbeitnow.py
│   │   ├── n_remoteok.py
│   │   └── n_jooble.py
│   │
│   ├── loaders/
│   │   ├── clickhouse_loader.py
│   │   ├── create_clickhouse_schema.py
│   │   └── refresh_marts.py
│   │
│   ├── pipelines/
│   │   ├── run_jobs_pipeline.py
│   │   └── combine_normalized_batches.py
│   │
│   └── utils/
│       ├── clickhouse.py
│       ├── jobs_schema.py
│       ├── quality.py
│       └── s3.py
│
├── tests/
│   ├── conftest.py
│   ├── test_common.py
│   ├── test_combine_normalized_batches.py
│   └── test_s3.py
│
├── Dockerfile.airflow
├── docker-compose.yml
├── docker-compose.airflow.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

# Running the Project

## 1. Install Python dependencies

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

---

## 2. Configure environment variables

Create:

```bash
cp .env.example .env
```

Configure the required API and infrastructure credentials.

Do not commit `.env`.

---

## 3. Start MinIO and ClickHouse

```bash
docker compose up -d
```

Check:

```bash
docker compose ps
```

---

## 4. Run the complete pipeline manually

```bash
uv run python -m src.pipelines.run_jobs_pipeline
```

The pipeline will:

```text
extract
→ normalize
→ store
→ combine
→ deduplicate
→ load
→ refresh marts
```

---

## 5. Run an individual source

Examples:

```bash
uv run python -m src.extractors.e_arbeitnow
uv run python -m src.extractors.e_remoteok
uv run python -m src.extractors.e_jooble
```

---

## 6. Start Airflow

```bash
docker compose -f docker-compose.airflow.yml up -d
```

Airflow UI:

```text
http://localhost:8080
```

---

## 7. Analytics Dashboard

Apache Superset is used as the BI layer and connects to the Job RADAR ClickHouse database.

Superset UI in the local development environment:

```text
http://localhost:8088
```

---

# Data Quality

Current quality checks include:

- missing titles;
- missing URLs;
- duplicate URLs;
- jobs without detected skills;
- filtering records without required fields;
- canonical schema validation before ClickHouse loading;
- exact deduplication during multi-source combination.

The project follows a fail-fast approach for unexpected API response structures.

---

# Design Principles

Job RADAR intentionally avoids unnecessary abstractions.

Current principles:

- source extractors are independent modules;
- source-specific normalization stays isolated;
- all sources return one canonical schema;
- SQL analytics remains outside Python;
- ClickHouse marts serve the BI layer;
- orchestration stays separate from business logic;
- changes are introduced in small, testable steps.

The project currently does not use extractor factories, inheritance hierarchies, or complex plugin systems.

---

---

# Documentation

Public project documentation:

- [Architecture](docs/architecture.md)
- [Portfolio Overview](docs/PORTFOLIO.md)
- [Roadmap](docs/roadmap.md)
- [v1.0.0 Release Checkpoint](docs/checkpoints/2026-08-02_v1.0.0_release.md)


# Roadmap

Version `v1.0.0` represents the first complete portfolio-ready release.

Future development is tracked in:

```text
docs/roadmap.md
```

Main future directions include:

- ATS integrations;
- improved normalization;
- stronger automated testing;
- source-level failure isolation;
- monitoring and alerting;
- deployment;
- advanced deduplication;
- additional dashboard analytics.

---

# Status

**v1.0.0 — released / portfolio-ready**

The first stable Job RADAR release is complete, tagged, and published.

Future work starts from the post-v1 roadmap rather than unfinished MVP scope.