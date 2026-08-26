import pandas as pd
import pytest

from src.pipelines.combine_normalized_batches import (
    combine_normalized_batches,
)


def make_df(rows):
    return pd.DataFrame(rows)


def test_combines_non_empty_dataframes():
    first = make_df([
        {
            "source": "arbeitnow",
            "source_job_id": "1",
            "url": "https://example.com/1",
        }
    ])
    second = make_df([
        {
            "source": "remoteok",
            "source_job_id": "2",
            "url": "https://example.com/2",
        }
    ])

    result = combine_normalized_batches([first, second])

    assert len(result) == 2
    assert set(result["source"]) == {"arbeitnow", "remoteok"}


def test_ignores_empty_dataframes():
    jobs = make_df([
        {
            "source": "arbeitnow",
            "source_job_id": "1",
            "url": "https://example.com/1",
        }
    ])

    result = combine_normalized_batches([pd.DataFrame(), jobs])

    assert len(result) == 1


def test_raises_when_no_dataframes_are_provided():
    with pytest.raises(ValueError, match="No normalized DataFrames provided"):
        combine_normalized_batches([])


def test_deduplicates_same_source_job_id():
    jobs = make_df([
        {
            "source": "arbeitnow",
            "source_job_id": "1",
            "url": "https://example.com/first",
        },
        {
            "source": "arbeitnow",
            "source_job_id": "1",
            "url": "https://example.com/second",
        },
    ])

    result = combine_normalized_batches([jobs])

    assert len(result) == 1
    assert result.iloc[0]["url"] == "https://example.com/first"


def test_deduplicates_same_url_across_sources():
    jobs = make_df([
        {
            "source": "arbeitnow",
            "source_job_id": "1",
            "url": "https://example.com/job",
        },
        {
            "source": "jooble",
            "source_job_id": "99",
            "url": "https://example.com/job",
        },
    ])

    result = combine_normalized_batches([jobs])

    assert len(result) == 1
    assert result.iloc[0]["source"] == "arbeitnow"
