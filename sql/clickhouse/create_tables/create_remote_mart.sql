CREATE TABLE IF NOT EXISTS job_radar.remote_mart
(
    work_format String,
    vacancies UInt64,
    unique_companies UInt64,
)
ENGINE = MergeTree
ORDER BY work_format;