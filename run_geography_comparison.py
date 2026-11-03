"""Run the original ZIP-point model and the HUD-weighted tract model."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data_preparation import prepare_model_data
from src.optimization import solve_with_gurobi, write_solution


def main() -> None:
    project_root = Path(__file__).resolve().parent
    cases = {
        "zip": project_root / "config" / "base_case.json",
        "tract": project_root / "config" / "tract_case.json",
    }
    rows: list[dict[str, object]] = []
    for geography, config_path in cases.items():
        print(f"Running {geography}-level demand case...")
        data = prepare_model_data(project_root, config_path)
        solution = solve_with_gurobi(data)
        output_dir = project_root / "results" / "geography_comparison" / geography
        write_solution(solution, output_dir)
        rows.append(
            {
                "demand_geography": geography,
                "demand_points": len(data.demand),
                "accessible_pairs": len(data.accessible_pairs),
                "baseline_demand_kwh": solution.summary["baseline_demand_kwh"],
                "projected_demand_kwh": solution.summary["projected_demand_kwh"],
                "total_served_kwh": solution.summary["total_served_kwh"],
                "selected_municipal_sites": solution.summary["selected_municipal_sites"],
                "additional_ports": solution.summary["additional_ports"],
                "investment_cost_usd": solution.summary["investment_cost_usd"],
                "all_checks_pass": solution.sanity_checks["all_checks_pass"],
            }
        )
    comparison = pd.DataFrame(rows)
    output_path = project_root / "results" / "geography_comparison" / "comparison.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(output_path, index=False)
    print(comparison.to_string(index=False))
    print(f"Wrote comparison to {output_path}")


if __name__ == "__main__":
    main()
