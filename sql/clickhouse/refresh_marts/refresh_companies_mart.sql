TRUNCATE TABLE job_radar.companies_mart;

INSERT INTO job_radar.companies_mart
SELECT
    company,
    count() AS vacancies,
    countIf(remote = true) AS remote_vacancies,
    countIf(remote = false) AS non_remote_vacancies,
    uniqExact(skill) AS unique_skills
FROM job_radar.jobs
ARRAY JOIN skills AS skill
WHERE company != ''
GROUP BY company;