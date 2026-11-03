"""Download the official HUD-USPS New York ZIP-to-tract crosswalk.

Create a free HUD USER API token, then set it only for the command being run:

    HUD_API_TOKEN=... python download_hud_crosswalk.py --year 2025 --quarter 4

The token is sent in the Authorization header and is never written to disk.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd


API_URL = "https://www.huduser.gov/hudapi/public/usps"


def _flatten_results(payload: dict[str, object]) -> tuple[list[dict[str, object]], dict[str, object]]:
    data = payload.get("data", payload)
    wrappers = data if isinstance(data, list) else [data]
    rows: list[dict[str, object]] = []
    metadata: dict[str, object] = {}
    for wrapper in wrappers:
        if not isinstance(wrapper, dict):
            continue
        metadata.update(
            {
                key: wrapper[key]
                for key in ["year", "quarter", "query", "input", "crosswalk_type"]
                if key in wrapper
            }
        )
        results = wrapper.get("results", [])
        if isinstance(results, dict):
            results = [results]
        for raw_row in results if isinstance(results, list) else []:
            if not isinstance(raw_row, dict):
                continue
            row = {str(key).lower(): value for key, value in raw_row.items()}
            input_value = str(wrapper.get("input", wrapper.get("query", ""))).zfill(5)
            if "zip" not in row and input_value.isdigit() and len(input_value) == 5:
                row["zip"] = input_value
            rows.append(row)
    return rows, metadata


def main() -> None:
    project_root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, help="HUD crosswalk year; omit for latest")
    parser.add_argument("--quarter", type=int, choices=[1, 2, 3, 4], help="Quarter; omit for latest")
    parser.add_argument("--query", default="NY", help="HUD state query; NY is the project default")
    parser.add_argument(
        "--output",
        type=Path,
        default=project_root / "data" / "hud_zip_tract_crosswalk.csv",
    )
    args = parser.parse_args()
    token = os.environ.get("HUD_API_TOKEN")
    if not token:
        raise SystemExit(
            "HUD_API_TOKEN is not set. Create a free token at "
            "https://www.huduser.gov/portal/dataset/uspszip-api.html and set it only "
            "for this command. Do not commit the token."
        )

    parameters: dict[str, object] = {"type": 1, "query": args.query}
    if args.year is not None:
        parameters["year"] = args.year
    if args.quarter is not None:
        parameters["quarter"] = args.quarter
    url = f"{API_URL}?{urlencode(parameters)}"
    request = Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    try:
        with urlopen(request, timeout=120) as response:
            payload = json.load(response)
    except HTTPError as exc:
        raise SystemExit(
            f"HUD API returned HTTP {exc.code}. Confirm that the token is valid and "
            "registered for the USPS Crosswalk API."
        ) from exc
    except URLError as exc:
        raise SystemExit(f"Could not reach the HUD API: {exc.reason}") from exc

    rows, api_metadata = _flatten_results(payload)
    table = pd.DataFrame(rows)
    if table.empty:
        raise SystemExit("HUD API returned no crosswalk rows")
    if "tract" not in table and "geoid" in table:
        table = table.rename(columns={"geoid": "tract"})
    required = {"zip", "tract", "res_ratio"}
    missing = required.difference(table.columns)
    if missing:
        raise SystemExit(
            f"HUD response is missing {sorted(missing)}. Returned columns: {sorted(table.columns)}"
        )
    table["zip"] = table["zip"].astype(str).str.extract(r"(\d+)", expand=False).str.zfill(5)
    table["tract"] = table["tract"].astype(str).str.extract(r"(\d+)", expand=False).str.zfill(11)
    table["res_ratio"] = pd.to_numeric(table["res_ratio"], errors="raise")
    table = table.sort_values(["zip", "tract"]).reset_index(drop=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(args.output, index=False)
    metadata = {
        "source": "HUD-USPS ZIP Code Crosswalk API",
        "source_url": url,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "crosswalk_direction": "ZIP-to-tract",
        "allocation_field": "res_ratio",
        "row_count": int(len(table)),
        **api_metadata,
    }
    metadata_path = args.output.with_name(args.output.stem + "_metadata.json")
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(f"Wrote {len(table):,} official crosswalk rows to {args.output}")
    print(f"Wrote source metadata to {metadata_path}")


if __name__ == "__main__":
    main()
