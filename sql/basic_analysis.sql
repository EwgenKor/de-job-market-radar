-- 1. Total vacancies
SELECT count() AS total_vacancies
FROM job_radar.jobs;


-- 2. Top skills
SELECT
    akill,
    count() AS vacancies
FROM job_radar.jobs
ARRAY JOIN skills AS skill
GROUP BY skill
ORDER BY vacancies DESC
LIMIT 20;


-- 3. Remote vs non-remote
SELECT
    remote,
    count() AS vacancies
FROM job_radar.jobs
GROUP BY remote
ORDER BY vacancies DESC;


-- 4. Top locations
SELECT
    location,
    count() AS vacancies
FROM job_radar.jobs
WHERE location != ''
GROUP BY location
ORDER BY vacancies DESC
LIMIT 20;


-- 5. Top companies
SELECT
    company,
    count() AS vacancies
FROM job_radar.jobs
WHERE company != ''
GROUP BY company
ORDER BY vacancies DESC
LIMIT 20;


-- 6. Vacancies with Python
SELECT
    title,
    company,
    location,
    remote,
    url
FROM job_radar.jobs
WHERE has(skills, 'python')
LIMIT 20;


-- 7. Vacancies with SQL
SELECT
    title,
    company,
    location,
    remote,
    url
FROM job_radar.jobs
WHERE has(skills, 'sql')
LIMIT 20;


-- 8. Vacancies with DE core stack
SELECT
    title,
    company,
    location,
    remote,
    skills
    url
FROM job_radar.jobs
WHERE hasAny(skills, ['python', 'sql', 'airflow', 'spark', 'kafka', 'dbt'])
LIMIT 30;


-- 9. Strong DE vacancies
SELECT
    title,
    company,
    location,
    remote,
    skills
    url
FROM job_radar.jobs
WHERE hasAny(skills, ['python', 'sql'])
  AND hasAny(skills, ['airflow', 'spark', 'kafka', 'dbt'])
LIMIT 30;


-- 10. Skill combination
SELECT
    skill_1,
    skill_2,
    count() AS vacancies
FROM job_radar.jobs
ARRAY JOIN skills AS skill_1
ARRAY JOIN skills AS skill_2
WHERE skill_1 < skill_2
GROUP BY
    skill_1,
    skill_2
ORDER BY vacancies DESC
LIMIT 20;


-- 11.Count vacancies by number of detected skills
SELECT
    lenght(skills) AS skills_count,
    count() AS vacancies
FROM job_radar.jobs
GROUP BY skills_count
ORDER BY skills_count;


-- 12. Jobs without detected skills

SELECT
    title,
    company,
    location,
    url
FROM job_radar.jobs
WHERE empty(skills)
LIMIT 30;


















