import logging

import pandas as pd


logger = logging.getLogger(__name__)


def combine_normalized_batches(dataframes: list[pd.DataFrame]) -> pd.DataFrame:
    if not dataframes:
        raise ValueError("No normalized DataFrames provided")

    non_empty_dataframes = [
        df
        for df in dataframes
        if not df.empty
    ]

    if not non_empty_dataframes:
        logger.warning(
            "All normalized DataFrames are empty"
        )

        return pd.DataFrame()

    combined_df = pd.concat(
        non_empty_dataframes,
        ignore_index=True,
    )

    rows_before_deduplication = len(combined_df)

    logger.info(
        "Combined %d normalized batches into %d rows",
        len(non_empty_dataframes),
        rows_before_deduplication,
    )

    combined_df = combined_df.drop_duplicates(
        subset=["source", "source_job_id"],
        keep="first",
    )

    source_duplicates_removed = (rows_before_deduplication - len(combined_df))

    rows_before_url_deduplication = len(combined_df)

    combined_df = combined_df.drop_duplicates(
        subset=["url"],
        keep="first",
    )

    url_duplicates_removed = (rows_before_url_deduplication - len(combined_df))

    combined_df = combined_df.reset_index(
        drop=True
    )

    logger.info(
        "Deduplication removed %d source duplicates and %d URL duplicates",
        source_duplicates_removed,
        url_duplicates_removed,
    )

    logger.info(
        "Final combined dataset contains %d rows",
        len(combined_df),
    )

    return combined_df
