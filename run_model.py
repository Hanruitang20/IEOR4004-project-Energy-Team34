"""Run the IEOR 4004 Milestone 4 base-case model."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.data_preparation import prepare_model_data
from src.optimization import solve_with_gurobi, write_solution


def main() -> None:
    project_root = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config", type=Path, default=project_root / "config" / "base_case.json"
    )
    parser.add_argument(
        "--output-dir", type=Path, default=project_root / "results" / "base_case"
    )
    parser.add_argument("--budget-usd", type=float)
    parser.add_argument("--equity-lambda", type=float)
    parser.add_argument("--service-radius-miles", type=float)
    parser.add_argument("--annual-growth-rate", type=float)
    parser.add_argument("--planning-horizon-years", type=int)
    args = parser.parse_args()

    overrides = {
        key: value
        for key, value in {
            "budget_usd": args.budget_usd,
            "equity_lambda": args.equity_lambda,
            "service_radius_miles": args.service_radius_miles,
            "annual_demand_growth_rate": args.annual_growth_rate,
            "planning_horizon_years": args.planning_horizon_years,
        }.items()
        if value is not None
    }
    data = prepare_model_data(project_root, args.config, overrides=overrides)
    print(
        f"Prepared {len(data.demand)} demand points, {len(data.sites)} supply sites, "
        f"and {len(data.accessible_pairs)} accessible pairs."
    )
    if len(data.excluded_candidates):
        print(f"Excluded {len(data.excluded_candidates)} municipal candidates after geocode checks.")
    solution = solve_with_gurobi(data)
    write_solution(solution, args.output_dir)
    print(f"Solver status: {solution.summary['solver_status']}")
    print(f"Selected sites: {solution.summary['selected_municipal_sites']}")
    print(f"Additional ports: {solution.summary['additional_ports']}")
    print(f"Investment cost: ${solution.summary['investment_cost_usd']:,.0f}")
    print(f"Total served: {solution.summary['total_served_kwh']:,.0f} kWh/week")
    print(f"Sanity checks pass: {solution.sanity_checks['all_checks_pass']}")
    print(f"Results written to {args.output_dir}")


if __name__ == "__main__":
    main()
