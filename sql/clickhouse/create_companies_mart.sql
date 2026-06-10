CREATE TABLE IF NOT EXISTS job_radar.companies_mart
(
    company String,
    vacancies UInt64,
    remote_vacancies UInt64,
    non_remote_vacancies UInt64,
    unique_skills UInt64
)
ENGINE = MergeTree
ORDER BY company;