CREATE TABLE IF NOT EXISTS job_radar.locations_mart
(
    location_raw String,
    vacancies UInt64,
    remote_vacancies UInt64,
    non_remote_vacancies UInt64,
    unique_companies UInt64
)
ENGINE = MergeTree
ORDER BY location_raw;