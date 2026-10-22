"""Download and clean rail-network validation data from IDFM."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import requests

DAILY_URL = (
    "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/"
    "validations-reseau-ferre-nombre-validations-par-jour-2eme-trimestre/records"
)
HOURLY_URL = (
    "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/"
    "validations-sur-le-reseau-ferre-profils-horaires-par-jour-type-2eme-trimestre/records"
)
ARCHIVE_URL = (
    "https://data.iledefrance-mobilites.fr/api/explore/v2.1/catalog/datasets/"
    "histo-validations-reseau-ferre/records"
)


def fetch_records(url: str, *, limit: int = 100, timeout: int = 30) -> list[dict[str, Any]]:
    """Fetch one page of records from an IDFM Explore API endpoint."""
    response = requests.get(url, params={"limit": limit}, timeout=timeout)
    response.raise_for_status()
    payload = response.json()
    return payload.get("results", payload if isinstance(payload, list) else [])


def clean_validations(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Flatten records and normalize dates and numeric validation columns."""
    frame = pd.json_normalize(records)
    if frame.empty:
        return frame
    for column in frame.columns:
        if any(token in column.lower() for token in ("date", "jour", "day")):
            frame[column] = pd.to_datetime(frame[column], errors="coerce")
        if any(token in column.lower() for token in ("validation", "nombre", "count")):
            frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame.drop_duplicates().reset_index(drop=True)


def download_and_clean(url: str, output: str | Path, *, limit: int = 100) -> pd.DataFrame:
    """Download one validation dataset, clean it, and write it as CSV."""
    frame = clean_validations(fetch_records(url, limit=limit))
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
    return frame


if __name__ == "__main__":
    download_and_clean(DAILY_URL, "data/navigo_validations_daily.csv")
