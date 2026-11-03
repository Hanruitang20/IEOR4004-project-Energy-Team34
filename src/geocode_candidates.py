"""Geocode NYC DOT municipal parking facilities and cache the result.

This script is intentionally separate from the optimization run. The model reads
the cached CSV so that normal runs are reproducible and do not depend on a live
geocoding service.
"""

from __future__ import annotations

import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd


GEOCODE_URL = (
    "https://geocode.arcgis.com/arcgis/rest/services/World/GeocodeServer/"
    "findAddressCandidates"
)
NYC_EXTENT = "-74.3,40.45,-73.65,40.95"


def geocode_address(address: str, timeout_seconds: int = 30) -> dict[str, object]:
    params = urllib.parse.urlencode(
        {
            "SingleLine": address,
            "f": "json",
            "outFields": "Match_addr,Addr_type",
            "maxLocations": 1,
            "searchExtent": NYC_EXTENT,
        }
    )
    request = urllib.request.Request(
        f"{GEOCODE_URL}?{params}",
        headers={"User-Agent": "IEOR4004-Team34-Milestone4/1.0"},
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        payload = json.load(response)

    candidates = payload.get("candidates", [])
    if not candidates:
        return {
            "latitude": None,
            "longitude": None,
            "geocode_score": None,
            "geocode_match_address": None,
            "geocode_address_type": None,
            "geocode_error": "No candidate returned",
        }

    candidate = candidates[0]
    attributes = candidate.get("attributes", {})
    location = candidate.get("location", {})
    return {
        "latitude": location.get("y"),
        "longitude": location.get("x"),
        "geocode_score": candidate.get("score"),
        "geocode_match_address": attributes.get("Match_addr", candidate.get("address")),
        "geocode_address_type": attributes.get("Addr_type"),
        "geocode_error": None,
    }


def normalize_nyc_address(address: str) -> str:
    """Improve NYC house-number matching without changing the source address."""
    query = re.sub(r"\s*\([^)]*\)\s*$", "", address).strip()
    # ArcGIS often interprets Queens hyphenated house numbers as subtraction.
    query = re.sub(r"^(\d+)-(\d+)\b", r"\1\2", query)
    return query


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        type=Path,
        default=project_root / "data" / "NYC_Municipal_Parking_Locations.xlsx",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root / "data" / "municipal_facilities_geocoded.csv",
    )
    parser.add_argument("--delay-seconds", type=float, default=0.15)
    args = parser.parse_args()

    facilities = pd.read_excel(args.input, sheet_name="Facilities", header=6)
    rows: list[dict[str, object]] = []
    for _, facility in facilities.iterrows():
        address = str(facility["Address / location"]).strip()
        query_address = normalize_nyc_address(address)
        record = {
            "facility_id": str(facility["Facility ID"]).strip(),
            "facility_name": str(facility["Facility name"]).strip(),
            "source_address": address,
            "geocode_query": query_address,
        }
        try:
            record.update(geocode_address(query_address))
        except Exception as exc:  # keep failures visible in the audit file
            record.update(
                {
                    "latitude": None,
                    "longitude": None,
                    "geocode_score": None,
                    "geocode_match_address": None,
                    "geocode_address_type": None,
                    "geocode_error": f"{type(exc).__name__}: {exc}",
                }
            )
        record["geocode_source"] = GEOCODE_URL
        rows.append(record)
        time.sleep(args.delay_seconds)

    output = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.output, index=False)
    failures = int(output["latitude"].isna().sum())
    print(f"Wrote {len(output)} geocodes to {args.output}; failures={failures}")


if __name__ == "__main__":
    main()
