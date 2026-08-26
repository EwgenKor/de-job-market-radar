# Job RADAR — Portfolio Overview

## Project

**Job RADAR** is a multi-source Data Engineering pipeline that collects job-market data from public APIs, normalizes heterogeneous payloads into a canonical schema, stores raw and processed datasets, loads analytics-ready data into ClickHouse, builds SQL marts, schedules the workflow with Airflow, and serves a Superset dashboard.

Stable release:

```text
v1.0.0
```

---

# Problem

Job-board APIs expose different schemas, identifiers, location formats, remote-work indicators, tags, timestamps, and response structures.

The project solves the engineering problem of turning those heterogeneous feeds into one reproducible analytical pipeline.

---

# Solution

```text
Arbeitnow + RemoteOK + Jooble
              ↓
       Python Extractors
              ↓
        Raw JSON / MinIO
              ↓
     Source Normalization
              ↓
      Canonical Job Schema
              ↓
        Quality Checks
              ↓
     Multi-source Combine
              ↓
        Deduplication
              ↓
          ClickHouse
              ↓
      7 Analytical Marts
              ↓
      Apache Superset
```

Airflow schedules and orchestrates the complete application pipeline.

---

# What I Built

## Multi-source ingestion

Integrated three different job-data APIs:

```text
Arbeitnow
RemoteOK
Jooble
```

Each source validates the external response contract before processing and preserves the original raw payload.

## Canonical normalization

Mapped heterogeneous source data to a shared schema with:

```text
source identity
job identity
company/title
raw location
normalized country
remote flag
normalized URL
tags
skills
source timestamp
extraction timestamp
batch identity
```

## Object storage

Implemented S3-compatible raw and processed layers using MinIO.

Paths are partitioned by:

```text
source
date
```

## Data quality

Added:

```text
missing-field checks
required-field filtering
duplicate checks
canonical schema validation
type casting
```

## Deduplication

Implemented deterministic two-stage deduplication using:

```text
(source, source_job_id)
normalized URL
```

## Analytical database

Loaded normalized jobs into ClickHouse and created seven SQL marts for:

```text
skills
remote work
companies
locations
skill pairs
daily market snapshots
daily country statistics
```

## Orchestration

Built an Airflow DAG with:

```text
daily schedule
retries
execution timeouts
max_active_runs control
PostgreSQL metadata DB
LocalExecutor
```

## BI

Connected Apache Superset to the ClickHouse analytical layer and built the first market overview dashboard.

---

# Dashboard

The dashboard includes:

- total vacancies;
- unique companies;
- detected skills;
- remote vacancies;
- daily market trend;
- remote vs non-remote distribution;
- top companies;
- top locations.

![Job RADAR Market Overview](images/job_radar_market_overview.png)

---

# Technology Stack

```text
Python 3.12
pandas
requests
python-dotenv
boto3
clickhouse-connect

Docker
Docker Compose

MinIO
ClickHouse

Apache Airflow 2.9.3
PostgreSQL
LocalExecutor

Apache Superset

Git
GitHub
```

---

# Engineering Decisions

The project deliberately avoids unnecessary complexity.

Examples:

- independent source modules instead of a premature extractor framework;
- SQL analytics kept in SQL files rather than embedded in Python;
- direct DataFrame loading between pipeline stages instead of unnecessary CSV re-reading;
- exact deterministic deduplication before fuzzy matching;
- Airflow used for orchestration while business logic remains independently runnable;
- Superset treated as an external BI tool rather than vendored into the repository.

---

# What the Project Demonstrates

This project demonstrates practical experience with:

```text
REST API integration
ETL/ELT pipeline design
data normalization
canonical schemas
data quality
S3-compatible object storage
batch traceability
deduplication
ClickHouse
SQL analytics
analytical marts
Airflow
Docker
BI integration
Git release workflow
technical documentation
```

---

# Current Limitations

Version `v1.0.0` is intentionally scoped as a portfolio-ready local data product.

Future improvements include:

- stronger automated tests;
- source failure isolation;
- richer normalization;
- better monitoring;
- direct ATS integrations;
- cloud deployment;
- additional BI analytics.

These are documented in `roadmap.md`.

---

# Release

```text
v1.0.0
```

The first stable version has been completed, tagged, and published as the portfolio baseline.
