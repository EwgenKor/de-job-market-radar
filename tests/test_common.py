from datetime import datetime, timezone

from src.normalizers.common import (
    build_batch_id,
    generate_source_job_id,
    normalize_country,
    normalize_url,
)


def test_normalize_url_removes_tracking_and_fragment():
    url = (
        "HTTPS://Example.COM/jobs/123/"
        "?utm_source=test&foo=bar#details"
    )

    assert normalize_url(url) == "https://example.com/jobs/123?foo=bar"


def test_generate_source_job_id_uses_existing_source_id():
    result = generate_source_job_id(
        source="arbeitnow",
        source_job_id=" job-123 ",
        url="https://example.com/jobs/123",
    )

    assert result == "job-123"


def test_generate_source_job_id_fallback_is_deterministic():
    first = generate_source_job_id(
        source="test_source",
        source_job_id=None,
        url="https://example.com/jobs/123?utm_source=one",
    )

    second = generate_source_job_id(
        source="test_source",
        source_job_id=None,
        url="https://example.com/jobs/123?utm_source=two",
    )

    assert first == second
    assert len(first) == 64


def test_normalize_country_handles_aliases():
    assert normalize_country("Berlin, Deutschland") == "Germany"
    assert normalize_country("United Kingdom") == "United Kingdom"
    assert normalize_country("Amsterdam, Holland") == "Netherlands"


def test_normalize_country_returns_empty_for_remote_locations():
    assert normalize_country("Remote") == ""
    assert normalize_country("Worldwide") == ""


def test_build_batch_id_uses_utc_timestamp_and_source():
    run_datetime = datetime(
        2026,
        8,
        2,
        17,
        30,
        45,
        tzinfo=timezone.utc,
    )

    assert build_batch_id("jooble", run_datetime) == "20260802173045Z_jooble"
