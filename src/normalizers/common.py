import hashlib
import re
from datetime import datetime, timezone
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


TRACKING_QUERY_PARAMS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
}


COUNTRY_ALIASES = {
    # Czechia
    "czech republic": "Czechia",
    "czechia": "Czechia",

    # France
    "france": "France",
    "france métropolitaine": "France",

    # Germany
    "germany": "Germany",
    "deutschland": "Germany",

    # Netherlands
    "netherlands": "Netherlands",
    "the netherlands": "Netherlands",
    "holland": "Netherlands",

    # Poland
    "poland": "Poland",
    "polska": "Poland",

    # Serbia
    "serbia": "Serbia",
    "srbija": "Serbia",

    # United Kingdom
    "united kingdom": "United Kingdom",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",

    # USA
    "united states": "USA",
    "united states of america": "USA",
    "usa": "USA",
    "u.s.a.": "USA",
    "us": "USA",
    "u.s.": "USA",
}


def build_batch_id(
    source: str,
    run_datetime: datetime | None = None,
) -> str:
    if run_datetime is None:
        run_datetime = datetime.now(timezone.utc)

    if run_datetime.tzinfo is None:
        run_datetime = run_datetime.replace(tzinfo=timezone.utc)

    timestamp = run_datetime.astimezone(timezone.utc).strftime("%Y%m%d%H%M%SZ")

    return f"{timestamp}_{source}"


def normalize_url(value: str | None) -> str:
    if not value:
        return ""

    url = value.strip()

    if not url:
        return ""

    parts = urlsplit(url)

    filtered_query = [
        (key, query_value)
        for key, query_value in parse_qsl(
            parts.query,
            keep_blank_values=True,
        )
        if key.lower() not in TRACKING_QUERY_PARAMS
    ]

    normalized_path = parts.path.rstrip("/") or "/"

    return urlunsplit(
        (
            parts.scheme.lower(),
            parts.netloc.lower(),
            normalized_path,
            urlencode(filtered_query),
            "",
        )
    )


def generate_source_job_id(
    source: str,
    source_job_id: str | int | None,
    url: str,
) -> str:
    if source_job_id is not None:
        clean_source_job_id = str(source_job_id).strip()

        if clean_source_job_id:
            return clean_source_job_id

    normalized_url = normalize_url(url)

    if not normalized_url:
        raise ValueError(
            "Cannot generate source_job_id without source ID or URL"
        )

    raw_value = f"{source}:{normalized_url}"

    return hashlib.sha256(
        raw_value.encode("utf-8")
    ).hexdigest()


def normalize_country(location_raw: str | None) -> str:
    if not location_raw:
        return ""

    location = re.sub(r"\s+", " ", location_raw).strip()

    if not location:
        return ""

    location_lower = location.lower()

    if location_lower in {
        "remote",
        "worldwide",
        "anywhere",
        "global",
    }:
        return ""

    last_part = location.rsplit(",", maxsplit=1)[-1].strip()
    last_part_lower = last_part.lower()

    if last_part_lower in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[last_part_lower]

    if location_lower in COUNTRY_ALIASES:
        return COUNTRY_ALIASES[location_lower]

    return last_part