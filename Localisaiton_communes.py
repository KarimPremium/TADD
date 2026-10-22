"""Retrieve geographic reference data for Île-de-France municipalities."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import requests

COMMUNES_URL = "https://geo.api.gouv.fr/communes"


def fetch_communes(
    *,
    fields: str = "nom,code,codeDepartement,population,centre",
    timeout: int = 30,
) -> list[dict[str, Any]]:
    """Fetch Île-de-France municipalities and their center coordinates."""
    response = requests.get(
        COMMUNES_URL,
        params={"codeRegion": "11", "fields": fields, "format": "json"},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def clean_communes(records: list[dict[str, Any]]) -> pd.DataFrame:
    """Flatten municipality records and normalize population values."""
    frame = pd.json_normalize(records)
    if "population" in frame:
        frame["population"] = pd.to_numeric(frame["population"], errors="coerce")
    return frame.drop_duplicates(subset=["code"] if "code" in frame else None).reset_index(
        drop=True
    )


def save_communes(records: list[dict[str, Any]], output: str | Path) -> pd.DataFrame:
    """Clean municipality records and save them as CSV."""
    frame = clean_communes(records)
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
    return frame


if __name__ == "__main__":
    save_communes(fetch_communes(), "data/idf_communes.csv")
