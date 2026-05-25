
import logging

import pandas as pd


logger = logging.getLogger(__name__)


def run_quality_checks(df: pd.DataFrame) -> None:
    missing_titles = df["title"].isna().sum()
    missing_urls = df["url"].isna().sum()
    duplicate_urls = df["url"].duplicated().sum()

    empty_skills = df["skills"].apply(len).eq(0).sum()


    logger.info("Missing titles: %s", missing_titles)
    logger.info("Missing urls: %s", missing_urls)
    logger.info("Jobs without skills: %s", empty_skills)

    if duplicate_urls >0:
        logger.warning("Duplicate urls: %s", duplicate_urls)


def filter_required_fields(df: pd.DataFrame) -> pd.DataFrame:
    return df[
        df["title"].notna()
        & df["url"].notna()
    ]