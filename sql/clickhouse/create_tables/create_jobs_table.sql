CREATE DATABASE IF NOT EXISTS job_radar;

CREATE TABLE IF NOT EXISTS job_radar.jobs
(
    batch_id String,
    source String,
    source_job_id String,
    title String,
    company String,
    location_raw String,
    country String,
    remote Bool,
    url String,
    tags Array(String),
    skills Array(String),
    created_at String,
    extracted_at DateTime64(3, 'UTC'),
    description String,
    loaded_at DateTime64(3, 'UTC')
)
ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY (source, source_job_id);