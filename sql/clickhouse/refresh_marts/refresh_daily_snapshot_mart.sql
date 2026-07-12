ALTER TABLE job_radar.daily_snapshot_mart
DELETE WHERE snapshot_date = today();

INSERT INTO job_radar.daily_snapshot_mart
SELECT
    today() AS snapshot_date,
    count() AS total_vacancies,
    countIf(remote = true) AS remote_vacancies,
    countIf(remote = false) AS non_remote_vacancies,
    uniqExact(company) AS unique_companies,
    (
        SELECT uniqExact(skill)
        FROM job_radar.jobs
        ARRAY JOIN skills AS skill
        WHERE skill != ''
    ) AS unique_skills
FROM job_radar.jobs FINAL;