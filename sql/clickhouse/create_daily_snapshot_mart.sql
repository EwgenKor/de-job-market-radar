CREATE TABLE IF NOT EXISTS job_radar.daily_snapshot_mart
(
    snapshot_date Date,
    total_vacancies UInt64,
    remote_vacancies UInt64,
    non_remote_vacancies UInt64,
    unique_companies UInt64,
    unique_skills UInt64
)
ENGINE = MergeTree
ORDER BY snapshot_date;