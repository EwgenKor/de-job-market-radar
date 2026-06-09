CREATE TABLE IF NOT EXISTS job_radar.skills_mart
(
    skill String,
    vacancies UInt64,
    remove_vacancies UInt64,
    non_remote_vacancies UInt64,
    unique_companies UInt64
)
ENGINE = MergeTree
ORDER BY skill;