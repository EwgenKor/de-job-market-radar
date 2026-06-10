import logging
import os

import clickhouse_connect
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)

load_dotenv()

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "")
CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "job_radar")


def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        database=CLICKHOUSE_DATABASE,
    )


def refresh_skills_mart(client) -> None:
    logger.info("Refreshing skills_mart...")

    client.command("TRUNCATE TABLE job_radar.skills_mart")

    client.command(
        """
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
        """
    )

    logger.info("skills_mart refreshed successfully")


def refresh_remote_mart(client) -> None:
    logger.info("Refreshing remote_mart...")

    client.command("TRUNCATE TABLE job_radar.remote_mart")

    client.command(
        """
        INSERT INTO job_radar.remote_mart
        SELECT
            if(remote = true, 'remote', 'non remote') AS work_format,
            count() AS vacancies,
            uniqExact(company) AS unique_companies
        FROM job_radar.jobs
        GROUP BY work_format;
        """
    )

    logger.info("remote_mart refreshed successfully")


def refresh_companies_mart(client) -> None:
    logger.info("Refreshing companies_mart...")

    client.command("TRUNCATE TABLE job_radar.companies_mart")

    client.command(
        """
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
        """
    )

    logger.info("companies_mart refreshed successfully")


def refresh_locations_mart(client) -> None:
    logger.info("Refreshing locations_mart")

    client.command("TRUNCATE TABLE job_radar.locations_mart")

    client.command(
        """
        INSERT INTO job_radar.locations_mart
        SELECT
            location,
            count() AS vacancies,
            countIf(remote = true) AS remote_vacancies,
            countIf(remote = false) AS non_remote_vacancies,
            uniqExact(company) AS unique_companies
        FROM job_radar.jobs
        WHERE location != ''
        GROUP BY location
        """
    )


def refresh_skill_pairs_mart(client) -> None:
    logger.info("Refreshing skill_pairs_mart")

    client.command("TRUNCATE TABLE job_radar.skill_pairs_mart")

    client.command(
        """
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
            skill_2
        """
    )


def refresh_daily_snapshot_mart(client) -> None:
    logger.info("Refreshing daily_snapshot_mart")

    client.command(
        """
        ALTER TABLE job_radar.daily_snapshot_mart
        DELETE WHERE snapshot_date = today()
        """
    )

    client.command(
        """
        INSERT INTO job_radar.daily_snapshot_mart
        SELECT
            today() AS snapshot_date,
            count() AS total_vacancies,
            countIf(remote = true) AS remote_vacancies,
            countIf(remote = false) AS non_remote_vacancies,
            uniqExact(company) AS unique_companies,
            uniqExact(skill) AS unique_skills
        FROM job_radar.jobs
        ARRAY JOIN skills AS skill
        """
    )


def refresh_daily_country_mart(client) -> None:
    logger.info("Refreshing daily_country_mart")

    client.command(
        """
        ALTER TABLE job_radar.daily_country_mart
        DELETE WHERE snapshot_date = today()
        """
    )

    client.command(
        """
        INSERT INTO job_radar.daily_country_mart
        SELECT
            today() AS snapshot_date,
            trim(splitByChar(',', location)[-1]) AS country,
            count() AS vacancies,
            countIf(remote = true) AS remote_vacancies,
            countIf(remote = false) AS non_remote_vacancies,
            uniqExact(company) AS unique_companies
        FROM job_radar.jobs
        WHERE location != ''
        GROUP BY country
        """
    )


def refresh_all_marts(client) -> None:

    refresh_skills_mart(client)
    refresh_remote_mart(client)
    refresh_companies_mart(client)
    refresh_locations_mart(client)
    refresh_skill_pairs_mart(client)
    refresh_daily_snapshot_mart(client)
    refresh_daily_country_mart(client)


def main() -> None:

    client = get_clickhouse_client()

    refresh_all_marts(client)


if __name__ == "__main__":
    main()