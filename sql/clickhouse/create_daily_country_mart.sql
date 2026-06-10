CREATE TABLE IF NOT EXISTS job_radar.daily_country_mart
(
    snapshot_date Date,
    country String,
    vacancies UInt64,
    non_remote_vacancies UInt64,
    onsite_vacancies UInt64,
    unique_companies UInt64
)
ENGINE = MergeTree
ORDER BY (snapshot_date, country);