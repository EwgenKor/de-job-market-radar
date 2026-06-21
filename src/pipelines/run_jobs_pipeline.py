import logging

from src.extractors.arbeitnow import run_extractor
from src.loaders.clickhouse_loader import run_loader
from src.loaders.refresh_marts import main as refresh_marts


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def run_jobs_pipeline() -> None:
    logger.info("Running Job Radar pipeline")

    logger.info("Step 1/3: Extract jobs")
    run_extractor()

    logger.info("Step 2/3: Load jobs to ClickHouse")
    run_loader()

    logger.info("Step 3/3: Refresh Marts")
    refresh_marts()

    logger.info("Job RADAR pipeline finished successfully")


def main() -> None:
    run_jobs_pipeline()


if __name__ == "__main__":
    main()