# Job RADAR — Architecture

## Overview

Job RADAR is a multi-source Data Engineering project for collecting, normalizing, storing, and analyzing job-market data.

The first stable release, `v1.0.0`, implements a complete local pipeline from external APIs to an analytical dashboard.

---

# High-Level Architecture

```text
                           EXTERNAL SOURCES
                 ┌────────────┬────────────┬────────────┐
                 │ Arbeitnow  │  RemoteOK  │   Jooble   │
                 └─────┬──────┴─────┬──────┴─────┬──────┘
                       │            │            │
                       └────────────┼────────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │ Source Extractors   │
                         │ src/extractors/     │
                         └──────────┬──────────┘
                                    │
                      ┌─────────────┴─────────────┐
                      │                           │
                      ▼                           ▼
             ┌────────────────┐          ┌──────────────────┐
             │ Raw JSON       │          │ Source Normalizer │
             │ local storage  │          │ src/normalizers/  │
             └───────┬────────┘          └─────────┬────────┘
                     │                             │
                     ▼                             ▼
             ┌────────────────┐          ┌──────────────────┐
             │ MinIO Raw      │          │ Canonical Schema │
             │ raw/source=... │          └─────────┬────────┘
             └────────────────┘                    │
                                                  ▼
                                         ┌──────────────────┐
                                         │ Quality Checks   │
                                         └─────────┬────────┘
                                                   │
                                      ┌────────────┴────────────┐
                                      │                         │
                                      ▼                         ▼
                             ┌────────────────┐        ┌──────────────────┐
                             │ Processed CSV  │        │ pandas DataFrame │
                             └───────┬────────┘        └─────────┬────────┘
                                     │                           │
                                     ▼                           │
                             ┌────────────────┐                   │
                             │ MinIO Processed│                   │
                             └────────────────┘                   │
                                                                 ▼
                                                   ┌────────────────────────┐
                                                   │ Combine Source Batches │
                                                   └────────────┬───────────┘
                                                                │
                                                                ▼
                                                   ┌────────────────────────┐
                                                   │ Exact Deduplication    │
                                                   │ source + source_job_id │
                                                   │ normalized URL         │
                                                   └────────────┬───────────┘
                                                                │
                                                                ▼
                                                   ┌────────────────────────┐
                                                   │ Schema Validation      │
                                                   └────────────┬───────────┘
                                                                │
                                                                ▼
                                                   ┌────────────────────────┐
                                                   │ ClickHouse             │
                                                   │ job_radar.jobs         │
                                                   └────────────┬───────────┘
                                                                │
                                                                ▼
                                                   ┌────────────────────────┐
                                                   │ Analytical Marts       │
                                                   │ 7 SQL marts            │
                                                   └────────────┬───────────┘
                                                                │
                                                                ▼
                                                   ┌────────────────────────┐
                                                   │ Apache Superset        │
                                                   │ Market Overview        │
                                                   └────────────────────────┘
```

Airflow orchestrates the application pipeline:

```text
┌──────────────────────────┐
│ Apache Airflow           │
│ job_radar_pipeline       │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ create_clickhouse_schema │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│ run_jobs_pipeline        │
└──────────────────────────┘
```

---

# Project Structure

```text
de_job_radar/
│
├── airflow/
│   └── dags/
│       └── job_radar_pipeline_dag.py
│
├── bi/
│   └── superset/
│       ├── README.md
│       └── exports/
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
│   ├── normalizers/
│   │   ├── common.py
│   │   ├── n_arbeitnow.py
│   │   ├── n_remoteok.py
│   │   └── n_jooble.py
│   ├── loaders/
│   │   ├── clickhouse_loader.py
│   │   ├── create_clickhouse_schema.py
│   │   └── refresh_marts.py
│   ├── pipelines/
│   │   ├── combine_normalized_batches.py
│   │   └── run_jobs_pipeline.py
│   └── utils/
│       ├── clickhouse.py
│       ├── jobs_schema.py
│       ├── quality.py
│       └── s3.py
│
├── tests/
│   ├── test_common.py
│   ├── test_combine_normalized_batches.py
│   └── test_s3.py
│
├── Dockerfile.airflow
├── docker-compose.yml
├── docker-compose.airflow.yml
├── requirements.txt
├── .env.example
├── README.md
└── README_RU.md
```

Generated data, local secrets, IDE metadata, and runtime logs are excluded from version control.

---

# Source Layer

Current sources:

```text
Arbeitnow
RemoteOK
Jooble
```

Each source is implemented as a standalone extractor.

Responsibilities:

```text
HTTP request
↓
response validation
↓
raw JSON persistence
↓
raw MinIO upload
↓
batch_id generation
↓
normalization
↓
quality checks
↓
processed CSV persistence
↓
processed MinIO upload
↓
return pd.DataFrame
```

This avoids coupling downstream processing to source-specific API formats.

---

# Fail-Fast API Validation

Each extractor validates the expected top-level response structure immediately after JSON parsing.

Examples:

```text
Arbeitnow → dictionary containing "data"
RemoteOK  → list
Jooble    → dictionary containing a "jobs" list
```

Unexpected source contracts raise an error rather than silently producing incomplete data.

---

# Normalization Layer

Source-specific normalizers convert heterogeneous API payloads to one canonical model.

Canonical fields:

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

Shared normalization utilities provide:

- `batch_id` generation;
- URL canonicalization;
- tracking-parameter removal;
- fallback `source_job_id` generation;
- basic country normalization.

Skill extraction is currently keyword-based and intentionally simple for v1.

---

# Data Quality

Source-level checks include:

```text
missing title count
missing URL count
duplicate URL count
jobs without detected skills
```

Rows without required source fields are filtered before downstream processing.

Before ClickHouse insertion, the canonical schema is validated and cast again.

Critical fields include:

```text
batch_id
source
source_job_id
title
url
```

---

# Storage Architecture

## Local Raw Layer

```text
data/raw/
```

Used for local inspection and debugging.

## Local Processed Layer

```text
data/processed/
```

Contains normalized CSV artifacts.

## MinIO

Object storage uses S3-compatible partitioned paths:

```text
raw/source=<source>/dt=<YYYY-MM-DD>/
processed/source=<source>/dt=<YYYY-MM-DD>/
```

---

# Multi-source Combination

The main runner collects source DataFrames:

```python
normalized_batches = [
    run_arbeitnow(),
    run_remoteok(),
    run_jooble(),
]
```

`combine_normalized_batches()`:

1. rejects a missing input list;
2. ignores empty source DataFrames;
3. concatenates successful normalized batches;
4. removes duplicate `(source, source_job_id)` records;
5. removes duplicate normalized URLs;
6. resets the resulting index.

The output is passed directly to the ClickHouse loader.

---

# ClickHouse Layer

Database:

```text
job_radar
```

Main table:

```text
jobs
```

The loader:

```text
combined DataFrame
↓
add loaded_at
↓
schema validation and type casting
↓
insert_df()
↓
ClickHouse
```

The loader also supports a CSV fallback mode for manual debugging or recovery.

---

# Analytical Marts

The SQL analytical layer consists of seven marts:

```text
skills_mart
remote_mart
companies_mart
locations_mart
skill_pairs_mart
daily_snapshot_mart
daily_country_mart
```

Responsibilities:

- `skills_mart` — demand for technical skills;
- `remote_mart` — remote vs non-remote distribution;
- `companies_mart` — company-level vacancy statistics;
- `locations_mart` — location-level statistics;
- `skill_pairs_mart` — technology co-occurrence;
- `daily_snapshot_mart` — market totals over time;
- `daily_country_mart` — country-level daily statistics.

Mart SQL remains outside Python under `sql/clickhouse/`.

---

# Airflow Orchestration

DAG:

```text
job_radar_pipeline
```

Schedule:

```text
0 8 * * *
```

Timezone:

```text
Europe/Podgorica
```

Flow:

```text
create_clickhouse_schema
↓
run_jobs_pipeline
```

Configuration:

```text
retries = 2
retry_delay = 2 minutes
max_active_runs = 1
catchup = False
```

The DAG intentionally does not duplicate application business logic.

---

# Docker Infrastructure

## Main Compose

`docker-compose.yml` provides:

```text
MinIO
ClickHouse
```

## Airflow Compose

`docker-compose.airflow.yml` provides:

```text
PostgreSQL
Airflow Init
Airflow Scheduler
Airflow Webserver
```

The two compose files remain separate because the data infrastructure and orchestration stack have different lifecycles during local development.

---

# BI Layer

Apache Superset is used as an external BI application connected to ClickHouse.

Dashboard:

```text
Job RADAR — Market Overview
```

Job RADAR stores only project-specific BI artifacts:

```text
bi/superset/exports/
docs/images/job_radar_market_overview.png
```

---

# Design Principles

The project intentionally favors explicit, understandable architecture over unnecessary abstraction.

Principles:

- independent source modules;
- one canonical downstream schema;
- source-specific transformation remains isolated;
- SQL analytics stays in SQL;
- orchestration stays outside business logic;
- deterministic deduplication before fuzzy matching;
- local infrastructure remains reproducible with Docker;
- each layer can be inspected independently.

Not used in v1:

```text
BaseExtractor
extractor factory
large inheritance hierarchy
Kafka
Spark
Kubernetes
microservices
```

These technologies would only be introduced if future requirements justify them.
