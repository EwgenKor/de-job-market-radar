import logging

import pandas as pd


logger = logging.getLogger(__name__)


def combine_normalized_batches(
    dataframes: list[pd.DataFrame],
) -> pd.DataFrame:
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

    logger.info(
        "Combined %d normalized batches into %d rows",
        len(non_empty_dataframes),
        len(combined_df),
    )

    return combined_df