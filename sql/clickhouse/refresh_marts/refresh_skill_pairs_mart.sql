TRUNCATE TABLE job_radar.skill_pairs_mart;

INSERT INTO job_radar.skill_pairs_mart
SELECT
    skill_1,
    skill_2,
    count() AS vacancies,
    countIf(remote = true) AS remote_vacancies,
    uniqExact(company) AS unique_companies
FROM job_radar.jobs
ARRAY JOIN skills AS skill_1
ARRAY JOIN skills AS skill_2
WHERE skill_1 < skill_2
GROUP BY
    skill_1,
    skill_2;