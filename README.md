# Job Market Analytics Pipeline

## Overview

Job Market Analytics Pipeline is a Data Engineering portfolio project focused on collecting, processing, and analyzing job postings for Data Engineering roles.

The project extracts job data from public APIs, stores raw responses, normalizes job fields, extracts technical skills, and prepares the data for further analytics.

## Project Goals

The main goals of this project are:

- collect job postings from public sources
- store raw job data
- normalize job fields into a structured format
- extract technical skills from job postings
- analyze demand for Data Engineering skills, tools, countries, and remote roles
- build a portfolio-ready Data Engineering pipeline

## Current Features

- Extracts job postings from the Arbeitnow API
- Saves raw API responses as JSON files
- Normalizes job data into a pandas DataFrame
- Handles missing and empty values
- Extracts technical skills from title, tags, and description
- Saves processed data as CSV

## Tech Stack

Current stack:

- Python 3.12
- requests
- pandas
- python-dotenv
- uv

Planned stack:

- Airflow
- MinIO / S3
- ClickHouse
- dbt
- Docker

## Current Architecture

Arbeitnow API
↓
Python extractor
↓
Raw JSON files
↓
Normalization layer
↓
Skills extraction
↓
Processed CSV dataset

## Planned Architecture

Multiple Job APIs
↓
Airflow DAGs
↓
MinIO / S3 raw layer
↓
ClickHouse staging tables
↓
dbt marts
↓
Analytics dashboard

## Project Structure

de_job_radar/
├── src/
│   └── extractors/
│       └── arbeitnow.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── sample/
├── docs/
├── notebooks/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── README_RU.md

## How to Run

Create and activate a virtual environment:

    uv venv
    source .venv/bin/activate

Install dependencies:

    uv pip install -r requirements.txt

Create a local environment file:

    cp .env.example .env

Run the extractor:

    python src/extractors/arbeitnow.py

## Output

Raw API responses are saved to:

data/raw/

Processed datasets are saved to:

data/processed/

Example processed fields:

source
title
company
location
remote
url
tags
skills
created_at
description

Roadmap
+ Create project structure
+ Add Arbeitnow API extractor
+ Save raw JSON data
+ Normalize job fields
+ Extract technical skills
+ Save processed CSV data
  Add logging
  Add tests
  Add more job sources
  Add Airflow orchestration
  Store raw data in MinIO / S3
  Load normalized data into ClickHouse
  Build dbt marts
  Build analytics dashboard

Status
The project is in active development.