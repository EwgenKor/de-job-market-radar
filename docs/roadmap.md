# Job RADAR — Roadmap

## Current Stable Release

```text
v1.0.0
```

Status:

```text
RELEASED / PORTFOLIO-READY
```

The original MVP is complete.

The roadmap below describes post-v1 development opportunities rather than unfinished release requirements.

---

# v1.0.0 — Completed

## Ingestion

- [x] Arbeitnow integration
- [x] RemoteOK integration
- [x] Jooble integration
- [x] fail-fast API response validation
- [x] independent source extractors
- [x] source-specific normalization

## Storage

- [x] raw JSON layer
- [x] processed CSV layer
- [x] MinIO / S3-compatible object storage
- [x] partitioned object paths by source and date

## Data Model

- [x] canonical job schema
- [x] `batch_id`
- [x] `source_job_id`
- [x] `extracted_at`
- [x] `loaded_at`
- [x] URL normalization
- [x] basic country normalization
- [x] technical-skill extraction

## Quality and Deduplication

- [x] missing-field checks
- [x] duplicate URL checks
- [x] required-field filtering
- [x] ClickHouse schema validation
- [x] exact `(source, source_job_id)` deduplication
- [x] exact normalized-URL deduplication

## Analytical Storage

- [x] ClickHouse
- [x] `jobs` table
- [x] seven analytical marts

## Orchestration

- [x] Apache Airflow
- [x] PostgreSQL metadata database
- [x] LocalExecutor
- [x] scheduled DAG
- [x] retries
- [x] active-run limit

## BI

- [x] Apache Superset integration
- [x] Market Overview dashboard
- [x] KPI cards
- [x] market trend chart
- [x] remote/non-remote distribution
- [x] top companies
- [x] top locations
- [x] dashboard screenshot
- [x] dashboard export

## Release

- [x] README
- [x] README_RU
- [x] architecture documentation
- [x] release checkpoint
- [x] Git tag `v1.0.0`

---

# Near-Term Improvements

## 1. Focused Automated Tests

Priority:

```text
HIGH
```

Targets:

- normalization utilities;
- deterministic job IDs;
- country normalization;
- multi-source combination;
- deduplication;
- canonical schema validation.

Avoid artificial coverage targets.

## 2. Source Failure Isolation

Priority:

```text
HIGH
```

Future behavior:

```text
Arbeitnow ── OK ───────┐
RemoteOK ── FAILED     ├→ continue with healthy sources
Jooble ──── OK ───────┘
```

Desired improvements:

- record source success/failure;
- continue when at least one source succeeds;
- fail if every source fails;
- make failed-source diagnostics explicit.

## 3. Better Source Observability

Track:

```text
rows fetched
rows normalized
rows rejected
rows deduplicated
execution duration
last successful run
failure reason
```

---

# Data Quality Improvements

## Country Normalization

Possible improvements:

```text
country aliases
city-to-country lookup
multi-location parsing
remote/worldwide handling
```

## Skill Extraction

Current implementation:

```text
keyword dictionary
```

Possible improvements:

```text
centralized skill dictionary
aliases
word-boundary matching
source-independent extraction module
validated LLM-assisted enrichment
```

## Advanced Deduplication

Current implementation:

```text
(source, source_job_id)
normalized URL
```

Possible future stages:

```text
stronger URL canonicalization
company + title + location signature
source priority
provenance preservation
optional fuzzy matching
```

---

# Analytics Improvements

## Skills & Technologies Dashboard

Possible second Superset page:

```text
Top Skills
Remote Skill Demand
Non-Remote Skill Demand
Skill Pairs
Skills Detail Table
```

## Source Analytics

Potential additions:

```text
vacancies by source
source contribution
source overlap
source freshness
source health
```

## Country Analytics

Improve location normalization before adding geographic maps.

---

# ATS Integration Track

A major future direction is direct ingestion from company Applicant Tracking Systems.

Proposed order:

```text
Greenhouse
↓
Lever
↓
Ashby
```

Possible later systems:

```text
Workable
SmartRecruiters
Teamtailor
BambooHR
```

The ATS work should first be validated as a separate integration track before changing the stable core architecture.

---

# Deployment Track

Goal:

```text
run Job RADAR independently of a developer laptop
```

Practical first deployment target:

```text
cloud VM
↓
Docker / Docker Compose
↓
Job RADAR pipeline
↓
ClickHouse / object storage
↓
Superset
```

Potential platform:

```text
AWS
```

Useful scope:

```text
IAM basics
EC2
security groups
SSH
Docker deployment
persistent volumes
```

Kubernetes is not currently justified.

---

# Optional API Layer

Possible stack:

```text
FastAPI
Pydantic
```

Potential endpoints:

```text
/skills
/companies
/trends
/jobs
/health
```

The purpose would be to expose existing analytical data, not to turn Job RADAR into a large backend application.

---

# Explicit Non-Goals

Do not add technologies solely for résumé keywords.

Not planned without a concrete need:

```text
Kafka
Spark
Kubernetes
Celery
microservice decomposition
complex extractor inheritance
large frontend application
heavy observability platform
```

---

# Prioritization Rule

A post-v1 feature should improve at least one of:

```text
reliability
data quality
analytical value
deployment value
portfolio value
```

If it does not, it stays in backlog.
