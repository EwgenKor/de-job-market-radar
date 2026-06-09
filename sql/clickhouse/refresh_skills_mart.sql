TRUNCATE TABLE job_radar.skills_mart;

INSERT INTO job_radar.skills_mart
SELECT
    skill,
    count() AS vacancies,
    countIf(remote = true) AS remote_vacancies,
    countIf(remote = false) AS non_remote_vacancies,
    uniqExact(company) AS unique_companies
FROM job_radar.jobs
ARRAY JOIN skills AS skill
WHERE skill != ''
GROUP BY skill;