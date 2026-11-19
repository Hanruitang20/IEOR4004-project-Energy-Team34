"""Section 6 sensitivity runs for the resident-curbside + municipal parking model.

Each scenario changes one input of the reference configuration
config/tract_resident_curbside_15m_cap150.json and re-optimizes both stages.
Every scenario writes its configuration and outputs to its own folder under
results/sensitivity_resident/. The reference results in
results/resident_curbside_15m_cap150/ are never overwritten.

Usage:
    python run_resident_sensitivity.py                 # all required scenarios
    python run_resident_sensitivity.py --only budget   # one analysis group
    python run_resident_sensitivity.py --include-radius
    python run_resident_sensitivity.py --summarize-only
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.data_preparation import load_config, prepare_model_data

PROJECT_ROOT = Path(__file__).resolve().parent
REFERENCE_CONFIG = PROJECT_ROOT / "config" / "tract_resident_curbside_15m_cap150.json"
OUTPUT_ROOT = PROJECT_ROOT / "results" / "sensitivity_resident"
PORTS_PER_SITE = 4
# Solver settings for every sensitivity run (including the re-solved reference).
# The checked-in reference used a 0.5% gap; differences between scenarios can be
# smaller than that tolerance, so all sensitivity runs use a 0.01% gap.
SOLVER_SETTINGS = {"mip_gap": 0.0001, "time_limit_seconds": 600}

# (group, scenario name, overrides). One parameter changes per scenario.
SCENARIOS: list[tuple[str, str, dict[str, object]]] = [
    ("reference", "reference", {}),
    *[("budget", f"budget_{label}", {"budget_usd": value})
      for label, value in [("3.75m", 3_750_000), ("7.5m", 7_500_000),
                           ("10m", 10_000_000), ("20m", 20_000_000)]],
    *[("curbside_cost", f"curbside_cost_{site // 1000}k",
       {"curbside_cost_per_port_usd": site / PORTS_PER_SITE})
      for site in [50_000, 75_000, 125_000, 150_000]],
    *[("demand", f"demand_{pct}pct", {"projected_demand_multiplier": pct / 100})
      for pct in [80, 120, 150]],
    *[("capacity", f"capacity_{pct}pct", {"curbside_availability_factor": pct / 100})
      for pct in [40, 80]],
    *[("equity", f"lambda_{lam}", {"equity_lambda": float(lam)}) for lam in [0, 2, 5]],
]
RADIUS_SCENARIOS = [
    ("radius", f"radius_{str(r).replace('.', 'p')}mi", {"service_radius_miles": r})
    for r in [0.25, 0.75, 1.0]
]
# Groups that also include the reference point when tabulated.
GROUP_REFERENCE_VALUE = {
    "budget": ("budget_usd", 15_000_000),
    "curbside_cost": ("curbside_site_cost_usd", 100_000),
    "demand": ("projected_demand_multiplier", 1.0),
    "capacity": ("curbside_availability_factor", 0.6),
    "equity": ("equity_lambda", 1.0),
    "radius": ("service_radius_miles", 0.5),
}


def reference_high_shortage_ids() -> set[str]:
    data = prepare_model_data(PROJECT_ROOT, REFERENCE_CONFIG)
    d = data.demand
    return set(d.loc[d["equity_shortage_score"] >= 1.0 - 1e-12, "demand_id"].astype(str))


def run_scenario(name: str, overrides: dict[str, object]) -> None:
    from src.optimization import solve_with_gurobi, write_solution

    out = OUTPUT_ROOT / name
    out.mkdir(parents=True, exist_ok=True)
    config = load_config(REFERENCE_CONFIG)
    config.update(SOLVER_SETTINGS)
    config.update(overrides)
    config["scenario_name"] = f"resident_sensitivity_{name}"
    config_path = out / "config.json"
    config_path.write_text(json.dumps(config, indent=2) + "\n")
    data = prepare_model_data(PROJECT_ROOT, config_path)
    solution = solve_with_gurobi(data)
    write_solution(solution, out)
    print(f"[{name}] {solution.summary['solver_status']} "
          f"served={solution.summary['total_served_kwh']:,.0f} "
          f"cost=${solution.summary['investment_cost_usd']:,.0f}")


def summarize(names: list[tuple[str, str]], high_ids: set[str]) -> pd.DataFrame:
    ref_dir = OUTPUT_ROOT / "reference"
    ref_curb = set(_selected(ref_dir, "curbside_candidate_solution.csv"))
    ref_muni = set(_selected(ref_dir, "municipal_candidate_solution.csv"))
    rows = []
    for group, name in names:
        out = OUTPUT_ROOT / name
        if not (out / "summary.json").exists():
            continue
        s = json.loads((out / "summary.json").read_text())
        cfg = json.loads((out / "config.json").read_text())
        checks = json.loads((out / "sanity_checks.json").read_text())
        dem = pd.read_csv(out / "demand_service_solution.csv", dtype={"demand_id": str})
        high = dem["demand_id"].astype(str).isin(high_ids)
        curb = set(_selected(out, "curbside_candidate_solution.csv"))
        muni = set(_selected(out, "municipal_candidate_solution.csv"))
        rows.append({
            "group": group,
            "scenario": name,
            "budget_usd": cfg["budget_usd"],
            "curbside_site_cost_usd": cfg["curbside_cost_per_port_usd"] * cfg["curbside_ports_per_site"]
            + cfg["curbside_fixed_cost_per_site_usd"],
            "projected_demand_multiplier": cfg.get("projected_demand_multiplier", 1.0),
            "curbside_availability_factor": cfg["curbside_availability_factor"],
            "equity_lambda": cfg["equity_lambda"],
            "service_radius_miles": cfg["service_radius_miles"],
            "projected_demand_kwh": s["projected_demand_kwh"],
            "served_kwh": s["total_served_kwh"],
            "service_rate": s["total_served_kwh"] / s["projected_demand_kwh"],
            "investment_usd": s["investment_cost_usd"],
            "unused_budget_usd": s["budget_slack_usd"],
            "municipal_investment_usd": s.get("municipal_investment_cost_usd"),
            "curbside_investment_usd": s.get("curbside_investment_cost_usd"),
            "municipal_sites": s["selected_municipal_sites"],
            "municipal_ports": s["additional_ports"],
            "curbside_sites": s["selected_curbside_sites"],
            "curbside_ports": s["curbside_ports"],
            "total_new_ports": s["additional_ports"] + s["curbside_ports"],
            "served_by_curbside_kwh": s.get("served_by_curbside_kwh"),
            "high_shortage_tracts": int(high.sum()),
            "high_shortage_service_rate": float(dem.loc[high, "served_kwh"].sum()
                                                / dem.loc[high, "projected_demand_kwh"].sum()),
            "other_tracts_service_rate": float(dem.loc[~high, "served_kwh"].sum()
                                               / dem.loc[~high, "projected_demand_kwh"].sum()),
            "curbside_sites_same_as_reference": len(curb & ref_curb),
            "curbside_sites_added_vs_reference": len(curb - ref_curb),
            "curbside_sites_dropped_vs_reference": len(ref_curb - curb),
            "municipal_sites_changed_vs_reference": len(muni ^ ref_muni),
            "stage1_status": s["primary_solver_status"],
            "stage1_mip_gap": s["primary_mip_gap"],
            "stage2_status": s["solver_status"],
            "stage2_mip_gap": s["final_mip_gap"],
            "all_checks_pass": checks["all_checks_pass"],
            "solver": s.get("solver"),
            "output_dir": str(out.relative_to(PROJECT_ROOT)),
        })
    return pd.DataFrame(rows)


def _selected(out: Path, filename: str) -> list[str]:
    df = pd.read_csv(out / filename, dtype={"site_id": str})
    return df.loc[df["selected"].astype(int).eq(1), "site_id"].astype(str).tolist()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", help="run one group, e.g. budget, curbside_cost, demand")
    parser.add_argument("--include-radius", action="store_true")
    parser.add_argument("--summarize-only", action="store_true")
    args = parser.parse_args()

    scenarios = SCENARIOS + (RADIUS_SCENARIOS if args.include_radius else [])
    if not args.summarize_only:
        for group, name, overrides in scenarios:
            if args.only and group not in (args.only, "reference"):
                continue
            if name == "reference" and (OUTPUT_ROOT / name / "summary.json").exists() and args.only:
                continue
            run_scenario(name, overrides)

    all_names = [(g, n) for g, n, _ in SCENARIOS + RADIUS_SCENARIOS]
    table = summarize(all_names, reference_high_shortage_ids())
    # Tabulate each group with the reference point included.
    blocks = []
    for group, (column, value) in GROUP_REFERENCE_VALUE.items():
        part = table.loc[table["group"].eq(group)]
        if part.empty:
            continue
        ref = table.loc[table["scenario"].eq("reference")].copy()
        ref["group"] = group
        blocks.append(pd.concat([part, ref]).sort_values(column))
    combined = pd.concat(blocks, ignore_index=True)
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_ROOT / "sensitivity_comparison.csv", index=False)
    print(f"Wrote {OUTPUT_ROOT / 'sensitivity_comparison.csv'} ({len(combined)} rows)")


if __name__ == "__main__":
    main()
