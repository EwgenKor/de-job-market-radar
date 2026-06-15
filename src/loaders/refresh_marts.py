import logging
import os
from pathlib import Path

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

SQL_DIR = Path("sql/clickhouse/refresh_marts")

REFRESH_SQL_FILES = [
    "refresh_skills_mart.sql",
    "refresh_remote_mart.sql",
    "refresh_companies_mart.sql",
    "refresh_locations_mart.sql",
    "refresh_skill_pairs_mart.sql",
    "refresh_daily_snapshot_mart.sql",
    "refresh_daily_country_mart.sql",
]


def get_clickhouse_client():
    return clickhouse_connect.get_client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        username=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        database=CLICKHOUSE_DATABASE,
    )


def run_sql_file(client, file_path: Path) -> None:
    logger.info("Running SQL file %s", file_path)

    sql = file_path.read_text(encoding="utf-8")

    statements = [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip()
    ]

    for statement in statements:
        client.command(statement)

    logger.info("SQL file executed successfully: %s", file_path)


def refresh_all_marts(client) -> None:
    for file_name in REFRESH_SQL_FILES:
        run_sql_file(client, SQL_DIR / file_name)


def main() -> None:
    client = get_clickhouse_client()
    refresh_all_marts(client)
    logger.info("All Marts refreshed successfully")


if __name__ == "__main__":
    main()