CREATE TABLE IF NOT EXISTS job_radar.skill_pairs_mart
(
    skill_1 String,
    skill_2 String,
    vacancies UInt64,
    remote_vacancies UInt64,
    unique_companies UInt64
)
ENGINE = MergeTree
ORDER BY (skill_1, skill_2);