"""Prepare Milestone 4 optimization inputs from the repository datasets."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


EARTH_RADIUS_MILES = 3958.7613


@dataclass
class ModelData:
    config: dict[str, object]
    demand: pd.DataFrame
    municipal: pd.DataFrame
    sites: pd.DataFrame
    accessible_pairs: pd.DataFrame
    excluded_candidates: pd.DataFrame
    audit: dict[str, object]


def load_config(path: Path) -> dict[str, object]:
    with path.open(encoding="utf-8") as stream:
        config = json.load(stream)
    required_positive = [
        "budget_usd",
        "weekly_energy_per_ev_kwh",
        "port_power_kw",
        "weekly_operating_hours",
        "incremental_port_cost_usd",
        "service_radius_miles",
    ]
    for key in required_positive:
        if float(config[key]) <= 0:
            raise ValueError(f"{key} must be positive")
    if not 0 <= float(config["public_l2_share"]) <= 1:
        raise ValueError("public_l2_share must be between 0 and 1")
    if not 0 <= float(config["availability_factor"]) <= 1:
        raise ValueError("availability_factor must be between 0 and 1")
    return config


def haversine_matrix_miles(
    left_lat: np.ndarray,
    left_lon: np.ndarray,
    right_lat: np.ndarray,
    right_lon: np.ndarray,
) -> np.ndarray:
    lat1 = np.radians(left_lat)[:, None]
    lon1 = np.radians(left_lon)[:, None]
    lat2 = np.radians(right_lat)[None, :]
    lon2 = np.radians(right_lon)[None, :]
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    value = np.sin(dlat / 2.0) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0) ** 2
    return 2.0 * EARTH_RADIUS_MILES * np.arcsin(np.sqrt(np.clip(value, 0.0, 1.0)))


def _calculate_energy_demand(
    demand: pd.DataFrame, config: dict[str, object]
) -> pd.DataFrame:
    demand = demand.copy()
    demand["baseline_demand_kwh"] = (
        demand["electric_registration_records"].astype(float)
        * float(config["weekly_energy_per_ev_kwh"])
        * float(config["public_l2_share"])
    )
    growth_multiplier = (1.0 + float(config["annual_demand_growth_rate"])) ** int(
        config["planning_horizon_years"]
    )
    demand["projected_demand_kwh"] = demand["baseline_demand_kwh"] * growth_multiplier
    return demand


def _load_zip_demand(
    data_dir: Path, config: dict[str, object]
) -> tuple[pd.DataFrame, dict[str, object]]:
    demand = pd.read_csv(data_dir / "dmv_electric_zip_summary_2026.csv", dtype={"zip": str})
    nyc_flag = demand["nyc_zip_lookup"].astype(str).str.lower().eq("true")
    coordinate_flag = demand["zcta_latitude"].notna() & demand["zcta_longitude"].notna()
    positive_flag = demand["electric_registration_records"].gt(0)
    audit = {
        "dmv_source_rows": int(len(demand)),
        "dmv_nyc_lookup_rows": int(nyc_flag.sum()),
        "dmv_nyc_rows_missing_zcta_coordinates": int((nyc_flag & ~coordinate_flag).sum()),
        "dmv_modeled_demand_points": int((nyc_flag & coordinate_flag & positive_flag).sum()),
    }
    demand = demand.loc[
        nyc_flag
        & coordinate_flag
        & positive_flag
    ].copy()
    demand["demand_id"] = "ZIP:" + demand["zip"].str.zfill(5)
    demand["demand_geography"] = "zip"
    demand["geography_id"] = demand["zip"].str.zfill(5)
    demand["latitude"] = demand["zcta_latitude"]
    demand["longitude"] = demand["zcta_longitude"]
    demand = _calculate_energy_demand(demand, config)
    return demand.reset_index(drop=True), audit


def _read_zip_tract_crosswalk(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"HUD ZIP-to-tract crosswalk not found: {path}. "
            "Create a free HUD USER API token and run `python download_hud_crosswalk.py`, "
            "or place an official ZIP_TRACT CSV/XLSX export at that path."
        )
    if path.suffix.lower() in {".xlsx", ".xls"}:
        crosswalk = pd.read_excel(path, dtype=str)
    else:
        crosswalk = pd.read_csv(path, dtype=str)
    crosswalk.columns = [str(column).strip().lower() for column in crosswalk.columns]
    zip_column = next(
        (column for column in ["zip", "zipcode", "zip_code"] if column in crosswalk),
        None,
    )
    tract_column = next(
        (column for column in ["tract", "geoid", "tract_geoid"] if column in crosswalk),
        None,
    )
    ratio_column = next(
        (column for column in ["res_ratio", "residential_ratio"] if column in crosswalk),
        None,
    )
    if not all([zip_column, tract_column, ratio_column]):
        raise ValueError(
            "The crosswalk must contain ZIP, TRACT/GEOID, and RES_RATIO columns. "
            f"Found: {sorted(crosswalk.columns)}"
        )
    result = crosswalk[[zip_column, tract_column, ratio_column]].rename(
        columns={
            zip_column: "zip",
            tract_column: "tract_geoid",
            ratio_column: "res_ratio",
        }
    )
    result["zip"] = result["zip"].str.extract(r"(\d+)", expand=False).str.zfill(5)
    result["tract_geoid"] = (
        result["tract_geoid"].str.extract(r"(\d+)", expand=False).str.zfill(11)
    )
    result["res_ratio"] = pd.to_numeric(result["res_ratio"], errors="coerce")
    result = result.dropna(subset=["zip", "tract_geoid", "res_ratio"])
    if result["res_ratio"].lt(0).any():
        raise ValueError("HUD RES_RATIO values must be nonnegative")
    return result.loc[result["res_ratio"].gt(0)].reset_index(drop=True)


def allocate_zip_demand_to_tracts(
    zip_demand: pd.DataFrame,
    crosswalk: pd.DataFrame,
    tract_attributes: pd.DataFrame,
    renormalize_over_nyc_tracts: bool = True,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Allocate NYC ZIP registration records to NYC tracts using HUD RES_RATIO.

    DMV rows in this project already represent NYC records, so each ZIP's ratios are
    normalized over matched NYC tracts. ZIPs with no positive NYC residential ratio
    remain unmatched rather than being assigned to an invented tract.
    """
    zip_demand = zip_demand.copy()
    zip_demand["zip"] = zip_demand["zip"].astype(str).str.zfill(5)
    tract_attributes = tract_attributes.copy()
    tract_attributes["tract_geoid"] = tract_attributes["tract_geoid"].astype(str).str.zfill(11)
    crosswalk = crosswalk.copy()
    crosswalk["zip"] = crosswalk["zip"].astype(str).str.zfill(5)
    crosswalk["tract_geoid"] = crosswalk["tract_geoid"].astype(str).str.zfill(11)

    nyc_crosswalk = crosswalk.merge(
        tract_attributes, on="tract_geoid", how="inner", validate="many_to_one"
    )
    nyc_crosswalk = nyc_crosswalk.loc[nyc_crosswalk["res_ratio"].gt(0)].copy()
    if nyc_crosswalk.empty:
        raise ValueError(
            "The HUD crosswalk has no positive RES_RATIO rows matching the NYC ACS tracts. "
            "Use a 2023 Q1 or later crosswalk based on 2020 Census tract geography."
        )
    nyc_ratio_sum = nyc_crosswalk.groupby("zip")["res_ratio"].sum().rename("nyc_res_ratio_sum")
    nyc_crosswalk = nyc_crosswalk.merge(nyc_ratio_sum, on="zip", validate="many_to_one")
    if renormalize_over_nyc_tracts:
        nyc_crosswalk["allocation_ratio"] = (
            nyc_crosswalk["res_ratio"] / nyc_crosswalk["nyc_res_ratio_sum"]
        )
    else:
        nyc_crosswalk["allocation_ratio"] = nyc_crosswalk["res_ratio"]

    allocation = zip_demand.merge(nyc_crosswalk, on="zip", how="inner", validate="one_to_many")
    allocation["allocated_registration_records"] = (
        allocation["electric_registration_records"].astype(float)
        * allocation["allocation_ratio"]
    )
    grouped = allocation.groupby("tract_geoid", as_index=False).agg(
        electric_registration_records=("allocated_registration_records", "sum"),
        source_zip_count=("zip", "nunique"),
        source_zips=("zip", lambda values: ";".join(sorted(set(values)))),
        raw_hud_res_ratio_sum=("res_ratio", "sum"),
    )
    grouped = grouped.merge(
        tract_attributes, on="tract_geoid", how="left", validate="one_to_one"
    )

    matched_zips = set(allocation["zip"])
    unmatched = zip_demand.loc[~zip_demand["zip"].isin(matched_zips)].copy()
    matched_source_records = float(
        zip_demand.loc[zip_demand["zip"].isin(matched_zips), "electric_registration_records"].sum()
    )
    allocated_records = float(grouped["electric_registration_records"].sum())
    audit: dict[str, object] = {
        "hud_crosswalk_rows_loaded": int(len(crosswalk)),
        "hud_crosswalk_rows_matched_to_nyc_tracts": int(len(nyc_crosswalk)),
        "dmv_nyc_positive_zip_rows": int(len(zip_demand)),
        "dmv_zip_rows_allocated_to_tracts": int(len(matched_zips)),
        "dmv_zip_rows_unmatched_in_crosswalk": int(len(unmatched)),
        "unmatched_zip_codes": sorted(unmatched["zip"].tolist()),
        "unmatched_electric_registration_records": float(
            unmatched["electric_registration_records"].sum()
        ),
        "matched_source_electric_registration_records": matched_source_records,
        "allocated_electric_registration_records": allocated_records,
        "allocation_conservation_error_records": allocated_records - matched_source_records,
        "tract_demand_points": int(len(grouped)),
        "renormalize_hud_res_ratio_over_nyc_tracts": renormalize_over_nyc_tracts,
        "minimum_pre_normalization_nyc_res_ratio_sum": float(nyc_ratio_sum.min()),
        "maximum_pre_normalization_nyc_res_ratio_sum": float(nyc_ratio_sum.max()),
        "allocation_note": (
            "RES_RATIO is normalized over matched NYC tracts because the DMV input contains "
            "NYC registration records; unmatched ZIPs are not imputed."
            if renormalize_over_nyc_tracts
            else "Raw HUD RES_RATIO is used without normalization; unmatched ZIPs are not imputed."
        ),
    }
    return grouped, audit


def _load_tract_demand(
    data_dir: Path, config: dict[str, object]
) -> tuple[pd.DataFrame, dict[str, object]]:
    source = pd.read_csv(
        data_dir / "dmv_electric_zip_summary_2026.csv", dtype={"zip": str}
    )
    nyc_flag = source["nyc_zip_lookup"].astype(str).str.lower().eq("true")
    positive_flag = source["electric_registration_records"].gt(0)
    zip_demand = source.loc[nyc_flag & positive_flag].copy()
    zip_demand["zip"] = zip_demand["zip"].str.zfill(5)

    tract_source = pd.read_csv(
        data_dir / "nyc_acs_vehicle_households_2020_2024.csv", dtype={"GEOID": str}
    )
    tract_attributes = tract_source.rename(
        columns={
            "GEOID": "tract_geoid",
            "NAME": "tract_name",
            "County": "county_name",
            "INTPTLAT": "latitude",
            "INTPTLONG": "longitude",
        }
    )[
        [
            "tract_geoid",
            "tract_name",
            "county_name",
            "households_with_vehicle",
            "latitude",
            "longitude",
        ]
    ]
    crosswalk_path = Path(str(config.get("zip_tract_crosswalk_path", "data/hud_zip_tract_crosswalk.csv")))
    if not crosswalk_path.is_absolute():
        crosswalk_path = data_dir.parent / crosswalk_path
    crosswalk = _read_zip_tract_crosswalk(crosswalk_path)
    demand, allocation_audit = allocate_zip_demand_to_tracts(
        zip_demand,
        crosswalk,
        tract_attributes,
        renormalize_over_nyc_tracts=bool(
            config.get("renormalize_hud_res_ratio_over_nyc_tracts", True)
        ),
    )
    demand["demand_id"] = "TRACT:" + demand["tract_geoid"]
    demand["demand_geography"] = "tract"
    demand["geography_id"] = demand["tract_geoid"]
    demand = _calculate_energy_demand(demand, config)
    audit: dict[str, object] = {
        "dmv_source_rows": int(len(source)),
        "dmv_nyc_lookup_rows": int(nyc_flag.sum()),
        "dmv_nyc_rows_missing_zcta_coordinates": int(
            (nyc_flag & (source["zcta_latitude"].isna() | source["zcta_longitude"].isna())).sum()
        ),
        "demand_geography": "tract",
        **allocation_audit,
    }
    return demand.reset_index(drop=True), audit


def _load_demand(
    data_dir: Path, config: dict[str, object]
) -> tuple[pd.DataFrame, dict[str, object]]:
    geography = str(config.get("demand_geography", "zip")).lower()
    if geography == "zip":
        demand, audit = _load_zip_demand(data_dir, config)
        audit["demand_geography"] = "zip"
        return demand, audit
    if geography == "tract":
        return _load_tract_demand(data_dir, config)
    raise ValueError("demand_geography must be either 'zip' or 'tract'")


def _reported_existing_ports(row: pd.Series) -> tuple[int, str]:
    if pd.notna(row["L2 spaces (explicit)"]):
        return int(row["L2 spaces (explicit)"]), "municipal_explicit_l2_count"
    evidence = str(row["L2 evidence"])
    if "L2 rate listed" in evidence and pd.notna(row["EV spaces (type unspecified)"]):
        return int(row["EV spaces (type unspecified)"]), "municipal_ev_count_with_l2_rate"
    return 0, "no_municipal_l2_count"


def _load_municipal(
    data_dir: Path,
    public_sites: pd.DataFrame,
    config: dict[str, object],
    port_capacity_kwh: float,
) -> tuple[pd.DataFrame, set[int], pd.DataFrame]:
    facilities = pd.read_excel(
        data_dir / "NYC_Municipal_Parking_Locations.xlsx",
        sheet_name="Facilities",
        header=6,
    )
    geocodes = pd.read_csv(data_dir / "municipal_facilities_geocoded.csv")
    facilities["facility_id"] = facilities["Facility ID"].astype(str).str.strip()
    municipal = facilities.merge(geocodes, on="facility_id", how="left", validate="one_to_one")

    minimum_score = float(config["minimum_geocode_score"])
    eligible = (
        municipal["latitude"].notna()
        & municipal["longitude"].notna()
        & municipal["geocode_score"].ge(minimum_score)
        & municipal["Parking spaces"].notna()
    )
    excluded = municipal.loc[~eligible].copy()
    municipal = municipal.loc[eligible].copy().reset_index(drop=True)

    reported = municipal.apply(_reported_existing_ports, axis=1)
    municipal["reported_existing_ports"] = [value[0] for value in reported]
    municipal["inventory_basis"] = [value[1] for value in reported]

    distances = haversine_matrix_miles(
        municipal["latitude"].to_numpy(float),
        municipal["longitude"].to_numpy(float),
        public_sites["latitude"].to_numpy(float),
        public_sites["longitude"].to_numpy(float),
    )
    nearest_index = distances.argmin(axis=1)
    nearest_distance = distances[np.arange(len(municipal)), nearest_index]
    match_radius = float(config["municipal_station_match_radius_miles"])
    is_match = nearest_distance <= match_radius

    municipal["matched_public_station_id"] = pd.NA
    municipal["matched_public_station_distance_miles"] = nearest_distance
    municipal["matched_public_ports"] = 0
    matched_ids: set[int] = set()
    for row_index, station_index in enumerate(nearest_index):
        if not is_match[row_index]:
            continue
        station = public_sites.iloc[int(station_index)]
        station_id = int(station["id"])
        matched_ids.add(station_id)
        municipal.at[row_index, "matched_public_station_id"] = station_id
        municipal.at[row_index, "matched_public_ports"] = int(station["ev_level2_evse_num"])

    municipal["existing_ports"] = municipal[
        ["reported_existing_ports", "matched_public_ports"]
    ].max(axis=1).astype(int)
    municipal["first_time_install_indicator"] = municipal["existing_ports"].eq(0).astype(int)
    remaining_spaces = (
        municipal["Parking spaces"].astype(int) - municipal["existing_ports"]
    ).clip(lower=0)
    municipal["max_additional_ports"] = np.minimum(
        int(config["max_additional_ports_per_site"]),
        np.floor(
            remaining_spaces * float(config["max_new_port_share_of_remaining_spaces"])
        ).astype(int),
    )
    municipal["site_id"] = "M:" + municipal["facility_id"]
    municipal["site_type"] = "municipal"
    municipal["site_name"] = municipal["Facility name"]
    municipal["existing_capacity_kwh"] = municipal["existing_ports"] * port_capacity_kwh
    municipal["added_port_capacity_kwh"] = port_capacity_kwh
    municipal["fixed_cost_usd"] = float(config["fixed_first_time_install_cost_usd"])
    municipal["port_cost_usd"] = float(config["incremental_port_cost_usd"])
    return municipal, matched_ids, excluded


def prepare_model_data(
    project_root: Path,
    config_path: Path,
    overrides: dict[str, object] | None = None,
) -> ModelData:
    data_dir = project_root / "data"
    config = load_config(config_path)
    if overrides:
        config.update(overrides)
    port_capacity_kwh = (
        float(config["port_power_kw"])
        * float(config["weekly_operating_hours"])
        * float(config["availability_factor"])
    )

    demand, demand_audit = _load_demand(data_dir, config)
    public_sites = pd.read_csv(data_dir / "nyc_public_operational_l2.csv")
    public_sites = public_sites.loc[
        public_sites["latitude"].notna()
        & public_sites["longitude"].notna()
        & public_sites["ev_level2_evse_num"].gt(0)
    ].copy()

    municipal, matched_ids, excluded = _load_municipal(
        data_dir, public_sites, config, port_capacity_kwh
    )
    other = public_sites.loc[~public_sites["id"].astype(int).isin(matched_ids)].copy()
    other["site_id"] = "O:" + other["id"].astype(int).astype(str)
    other["site_type"] = "other"
    other["site_name"] = other["station_name"]
    other["existing_ports"] = other["ev_level2_evse_num"].astype(int)
    other["existing_capacity_kwh"] = other["existing_ports"] * port_capacity_kwh
    other["added_port_capacity_kwh"] = 0.0

    site_columns = [
        "site_id",
        "site_type",
        "site_name",
        "latitude",
        "longitude",
        "existing_ports",
        "existing_capacity_kwh",
        "added_port_capacity_kwh",
    ]
    sites = pd.concat([municipal[site_columns], other[site_columns]], ignore_index=True)
    if sites["site_id"].duplicated().any():
        raise ValueError("Duplicate physical site IDs remain after municipal/public matching")

    distance_matrix = haversine_matrix_miles(
        demand["latitude"].to_numpy(float),
        demand["longitude"].to_numpy(float),
        sites["latitude"].to_numpy(float),
        sites["longitude"].to_numpy(float),
    )
    demand_index, site_index = np.where(
        distance_matrix <= float(config["service_radius_miles"]) + 1e-12
    )
    accessible = pd.DataFrame(
        {
            "demand_id": demand.iloc[demand_index]["demand_id"].to_numpy(),
            "site_id": sites.iloc[site_index]["site_id"].to_numpy(),
            "distance_miles": distance_matrix[demand_index, site_index],
        }
    )
    capacity_by_site = sites.set_index("site_id")["existing_capacity_kwh"]
    accessible["existing_capacity_kwh"] = accessible["site_id"].map(capacity_by_site)
    accessible_supply = accessible.groupby("demand_id")["existing_capacity_kwh"].sum()
    demand["accessible_existing_supply_kwh"] = (
        demand["demand_id"].map(accessible_supply).fillna(0.0)
    )
    demand["equity_shortage_score"] = np.maximum(
        0.0,
        1.0
        - demand["accessible_existing_supply_kwh"] / demand["baseline_demand_kwh"],
    ).clip(upper=1.0)

    audit = {
        **demand_audit,
        "public_l2_source_rows": int(len(public_sites)),
        "municipal_source_rows": int(len(municipal) + len(excluded)),
        "municipal_modeled_candidates": int(len(municipal)),
        "municipal_excluded_after_geocode_checks": int(len(excluded)),
        "municipal_candidates_matched_to_public_station": int(len(matched_ids)),
        "modeled_supply_sites_after_deduplication": int(len(sites)),
        "accessible_pairs": int(len(accessible)),
    }

    return ModelData(
        config=config,
        demand=demand,
        municipal=municipal,
        sites=sites,
        accessible_pairs=accessible,
        excluded_candidates=excluded,
        audit=audit,
    )
