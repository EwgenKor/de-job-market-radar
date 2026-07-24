TRUNCATE TABLE job_radar.locations_mart;

INSERT INTO job_radar.locations_mart
SELECT
    location_raw,
    count() AS vacancies,
    countIf(remote = true) AS remote_vacancies,
    countIf(remote = false) AS non_remote_vacancies,
    uniqExact(company) AS unique_companies
FROM job_radar.jobs
WHERE location_raw != ''
GROUP BY location_raw;