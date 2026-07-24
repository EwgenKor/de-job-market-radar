import logging

from src.extractors.e_arbeitnow import run_extractor
from src.loaders.clickhouse_loader import run_loader
from src.loaders.refresh_marts import main as refresh_marts
from src.pipelines.combine_normalized_batches import combine_normalized_batches


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def run_jobs_pipeline() -> None:
    logger.info("Running Job Radar pipeline")

    logger.info("Step 1/4: Extract and normalize sources")
    normalized_batches = [run_extractor()]

    logger.info("Step 2/4: Combine normalized batches")

    combined_df = combine_normalized_batches(normalized_batches)

    logger.info(
        "Combined normalized dataset contains %d rows",
        len(combined_df),
    )

    logger.info("Step 3/4: Load jobs to ClickHouse")
    run_loader(combined_df)

    logger.info("Step 4/4: Refresh Marts")
    refresh_marts()

    logger.info("Job RADAR pipeline finished successfully")


def main() -> None:
    run_jobs_pipeline()


if __name__ == "__main__":
    main()