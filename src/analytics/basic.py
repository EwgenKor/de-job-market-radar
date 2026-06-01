import ast
import logging
from  pathlib import Path

import pandas as pd


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(__name__)


def get_latest_processed_file() -> Path:
    processed_files = sorted(Path("data/processed").glob("jobs_normalized_*.csv"))

    if not processed_files:
        raise FileNotFoundError("No processed files found in data/processed")

    return processed_files[-1]


def load_processed_jobs(file_path, Path) -> pd.DataFrame:
    logger.info(f"Loading processed jobs from %s", file_path)

    df = pd.read_csv(file_path)

    logger.info("Loaded %s rows", len(df))

    return df


def parse_skills_column(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["skills"] = df["skills"].apply(
        lambda value: ast.literal_eval(value) if isinstance(value, str) else []
    )

    return df


def show_top_skills(df: pd.DataFrame, top_n: int = 10) -> None:
    skills = df["skills"].explode()

    skills = skills.dropna()

    logger.info("Top %s skills:", top_n)
    print(skills.value_counts().head(top_n))


def show_remote_distribution(df: pd.DataFrame) -> None:
    logger.info("Remote distribution:")
    print(df["remote"].value_counts(dropna=False))


def show_top_locations(df: pd.DataFrame, top_n: int = 10) -> None:
    logger.info("Top %s locations:", top_n)
    print(df["location"].value_counts(dropna=False).head(top_n))


def show_jobs_without_skills(df: pd.DataFrame) -> None:
    jobs_without_skills = df[df["skills"].apply(len).eq(0)]

    logger.info("Jobs without detected skills: %s", len(jobs_without_skills))

    print(jobs_without_skills["title", "company", "location", "url"].head(10))


def main() -> None:
    latest_file = get_latest_processed_file()

    df = load_processed_jobs(latest_file)
    df = parse_skills_column(df)

    show_top_skills(df)
    show_remote_distribution(df)
    show_top_locations(df)
    show_jobs_without_skills(df)


if __name__ == "__main__":
    main()
