ALTER TABLE job_radar.daily_country_mart
DELETE WHERE snapshot_date = today();

SELECT
    today() AS snapshot_date,
    trim(splitByChar(',', location)[-1]) AS country,
    count() AS vacancies,
    countIf(remote = true) AS remote_vacancies,
    countIf(remote = false) AS non_remote_vacancies,
    uniqExact(company) AS unique_companies
FROM job_radar.jobs
WHERE location != ''
GROUP BY country;