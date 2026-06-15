TRUNCATE TABLE job_radar.remote_mart;

INSERT INTO job_radar.remote_mart
SELECT
    if(remote = true, 'remote', 'non remote') AS work_format,
    count() AS vacancies,
    uniqExact(company) AS unique_companies
FROM job_radar.jobs
GROUP BY work_format;