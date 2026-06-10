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


def refresh_skills_mart() -> None:
    client = get_clickhouse_client()

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


def main() -> None:
    refresh_skills_mart()


if __name__ == "__main__":
    main()