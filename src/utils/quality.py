from multiprocessing.reduction import duplicate

import pandas as pd


def run_quality_checks(df: pd.DataFrame) -> None:
    missing_titles = df["title"].isna().sum()
    missing_urls = df["url"].isna().sum()
    duplicate_urls = df["url"].duplicated().sum()

    empty_skills = df["skill"].apply(len).eq(0).sum()

    print("\nDATA QUALITY REPORT")
    print("-" * 30)

    print(f"Missing titles: {missing_titles}")
    print(f"Missing urls: {missing_urls}")
    print(f"Duplicate urls: {duplicate_urls}")
    print(f"Jobs without skills: {empty_skills}")


def filter_required_fields(df: pd.DataFrame) -> pd.DataFrame:
    return df[
        df["title"].notna()
        & df["url"].notna()
    ]