SELECT
    today() AS snapshot_date,
    count() AS total_vacancies,
    countIf(remote = true) AS remote_vacancies,
    countIf(remote = false) AS non_remote_vacancies,
    uniqExact(company) AS unique_companies,
    uniqExact(skill) AS unique_skills
FROM job_radar.jobs
ARRAY JOIN skills AS skill;