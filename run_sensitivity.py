"""Run compact sanity-check scenarios for the first working model."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data_preparation import prepare_model_data
from src.optimization import solve_with_gurobi, write_solution


def main() -> None:
    project_root = Path(__file__).resolve().parent
    config_path = project_root / "config" / "base_case.json"
    output_root = project_root / "results" / "sensitivity"
    scenarios = {
        "unweighted": {"scenario_name": "unweighted", "equity_lambda": 0.0},
        "low_budget": {"scenario_name": "low_budget", "budget_usd": 2_250_000.0},
        "high_budget": {"scenario_name": "high_budget", "budget_usd": 5_250_000.0},
        "zero_growth": {
            "scenario_name": "zero_growth",
            "annual_demand_growth_rate": 0.0,
        },
        "one_mile_radius": {
            "scenario_name": "one_mile_radius",
            "service_radius_miles": 1.0,
        },
    }

    rows: list[dict[str, object]] = []
    for name, overrides in scenarios.items():
        print(f"Running {name}...")
        data = prepare_model_data(project_root, config_path, overrides=overrides)
        solution = solve_with_gurobi(data)
        write_solution(solution, output_root / name)
        row = dict(solution.summary)
        row.pop("data_audit", None)
        row["all_sanity_checks_pass"] = solution.sanity_checks["all_checks_pass"]
        rows.append(row)

    comparison = pd.DataFrame(rows).sort_values("scenario_name")
    output_root.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(output_root / "scenario_comparison.csv", index=False)

    budgets = comparison.loc[
        comparison["scenario_name"].isin(["low_budget", "high_budget"])
    ].set_index("scenario_name")
    if budgets.at["high_budget", "primary_objective_equity_weighted_kwh"] + 1e-6 < budgets.at[
        "low_budget", "primary_objective_equity_weighted_kwh"
    ]:
        raise AssertionError("Objective decreased when the budget increased")
    if not comparison["all_sanity_checks_pass"].all():
        raise AssertionError("At least one sensitivity scenario failed a feasibility check")
    print(comparison.to_string(index=False))
    print(f"Wrote sensitivity results to {output_root}")


if __name__ == "__main__":
    main()
