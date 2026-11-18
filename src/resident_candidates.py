"""Load the screened public-resident suggestion snapshot without inventing locations."""
from __future__ import annotations
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd


def load_resident_candidates(path: Path) -> pd.DataFrame:
    source = pd.read_csv(path, dtype={"location_id": str})
    required = {"location_id", "address", "latitude", "longitude", "wanted_count",
                "candidate_eligible", "exclusion_reason", "source_url", "borough_from_coordinates"}
    missing = required.difference(source.columns)
    if missing:
        raise ValueError(f"Resident candidate CSV missing columns: {sorted(missing)}")
    if source["location_id"].isna().any() or source["location_id"].duplicated().any():
        raise ValueError("Resident location IDs must be populated and unique")
    flags = source["candidate_eligible"].astype(str).str.lower()
    if not flags.isin(["true", "false"]).all():
        raise ValueError("candidate_eligible must contain explicit true/false values")
    chosen = source.loc[flags.eq("true")].copy()
    if chosen.empty:
        raise ValueError("No eligible resident curbside candidates remain")
    for name in ["latitude", "longitude", "wanted_count"]:
        chosen[name] = pd.to_numeric(chosen[name], errors="raise")
        if not np.isfinite(chosen[name]).all():
            raise ValueError(f"Resident candidate {name} must be finite")
    if not chosen["latitude"].between(-90, 90).all() or not chosen["longitude"].between(-180, 180).all():
        raise ValueError("Invalid resident candidate coordinates")
    if not chosen["wanted_count"].gt(0).all():
        raise ValueError("Eligible resident candidates require a published Wanted record")
    if chosen["borough_from_coordinates"].isna().any():
        raise ValueError("Eligible resident coordinates require a borough boundary match")
    chosen["site_id"] = "C:" + chosen["location_id"]
    chosen["site_name"] = "Resident suggestion: " + chosen["address"].fillna(chosen["location_id"])
    county = {"Bronx": "Bronx County", "Brooklyn": "Kings County", "Manhattan": "New York County",
              "Queens": "Queens County", "Staten Island": "Richmond County"}
    chosen["county_name"] = chosen["borough_from_coordinates"].map(county)
    if chosen["county_name"].isna().any():
        raise ValueError("Unexpected borough label in resident candidate data")
    excluded = source.loc[~flags.eq("true")]
    chosen = chosen.reset_index(drop=True)
    chosen.attrs["resident_candidate_audit"] = {
        "resident_source_locations": int(len(source)),
        "resident_eligible_candidates": int(len(chosen)),
        "resident_excluded_locations": int(len(excluded)),
        "resident_exclusion_reason_counts": excluded["exclusion_reason"].fillna("unspecified").value_counts().to_dict(),
        "resident_source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "resident_candidate_rule": "Published support present, original pin inside official NYC borough boundary, no explicit borough-text conflict; construction feasibility unverified",
    }
    return chosen
