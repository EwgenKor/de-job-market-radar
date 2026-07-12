CREATE DATABASE IF NOT EXISTS job_radar;

CREATE TABLE IF NOT EXISTS job_radar.jobs
(
    source String,
    title String,
    company String,
    location String,
    remote Bool,
    url String,
    tags Array(String),
    skills Array(String),
    created_at String,
    description String,
    loaded_at DateTime
)
ENGINE = ReplacingMergeTree(loaded_at)
ORDER BY (source, url);