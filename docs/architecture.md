# Architecture

## Overview

This project collects and analyzes Data Engineering job postings.

Right now the pipeline:

- fetches вакансии from the Arbeitnow API
- stores raw API responses locally
- normalizes job data
- extracts technical skills
- saves processed datasets for future analytics

The project is being built incrementally as a personal Data Engineering portfolio project.

---

## Current Flow

Arbeitnow API

-> Python extractor

-> Raw JSON data

-> Normalization

-> Skill extraction

-> Processed dataset

---

## Current Components

### Extractor

Location:
`src/extractors/arbeitnow.py`

Responsibilities:

- send API requests
- validate responses
- parse JSON
- save raw data

Raw data path:

`data/raw/`

---

### Raw Data Layer

Location:
`data/raw/`

Stores original API responses without modifications.

Raw data is excluded from Git because files can become large and temporary.

---

### Normalization Layer

Converts raw API data into a consistent structure.

Current fields:

- source
- title
- company
- location
- remote
- url
- tags
- skills
- created_at
- description

Also handles basic cleaning:

- remove empty values
- normalize tags
- filter broken records
- extract skills

---

### Skill Extraction

Skills are extracted using keyword matching.

Current examples:

- python
- sql
- airflow
- spark
- kafka
- dbt
- docker
- clickhouse
- postgres

Extracted skills are stored as a normalized list.

Example:

`["python", "sql", "airflow"]`

---

## Planned Flow

Multiple APIs

-> Airflow

-> MinIO / S3

-> ClickHouse

-> dbt

-> Analytics

-> Dashboard

---

## Planned Components

### Airflow

Will orchestrate pipeline tasks:

- schedule extraction
- manage dependencies
- retry failed tasks
- monitor pipeline runs

---

### MinIO / S3

Will store raw data in object storage.

---

### ClickHouse

Will store normalized analytical data.

Main use cases:

- skill analytics
- remote job analytics
- country analytics
- trend analysis

---

### dbt

Will transform raw analytical tables into marts for reporting and analytics.

---

## Design Principles

- keep raw data unchanged
- separate extraction from transformation
- keep secrets outside the codebase
- avoid committing generated data
- build incrementally