"""Gurobi implementation of the Milestone 3 algebraic formulation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .data_preparation import ModelData


@dataclass
class Solution:
    summary: dict[str, object]
    municipal: pd.DataFrame
    demand: pd.DataFrame
    site_utilization: pd.DataFrame
    sanity_checks: dict[str, object]
    curbside: pd.DataFrame | None = None


def _status_name(gp, status: int) -> str:
    names = {
        gp.GRB.OPTIMAL: "OPTIMAL",
        gp.GRB.TIME_LIMIT: "TIME_LIMIT",
        gp.GRB.INFEASIBLE: "INFEASIBLE",
        gp.GRB.INF_OR_UNBD: "INF_OR_UNBD",
        gp.GRB.UNBOUNDED: "UNBOUNDED",
    }
    return names.get(status, f"STATUS_{status}")


def solve_with_gurobi(data: ModelData) -> Solution:
    try:
        import gurobipy as gp
    except ImportError as exc:
        raise RuntimeError(
            "gurobipy is not installed. Run `pip install -r requirements.txt`."
        ) from exc

    demand = data.demand.set_index("demand_id", drop=False)
    municipal = data.municipal.set_index("site_id", drop=False)
    sites = data.sites.set_index("site_id", drop=False)
    pairs = data.accessible_pairs.reset_index(drop=True)
    config = data.config

    model = gp.Model("ieor4004_ev_charging")
    model.Params.MIPGap = float(config["mip_gap"])
    model.Params.TimeLimit = float(config["time_limit_seconds"])

    y = {
        site_id: model.addVar(vtype=gp.GRB.BINARY, name=f"y[{site_id}]")
        for site_id in municipal.index
    }
    x = {
        site_id: model.addVar(
            vtype=gp.GRB.INTEGER,
            lb=0,
            ub=int(municipal.at[site_id, "max_additional_ports"]),
            name=f"x[{site_id}]",
        )
        for site_id in municipal.index
    }
    # Curbside extension: w[k] = 1 opens candidate k with a fixed block of ports.
    curbside = (
        data.curbside.set_index("site_id", drop=False)
        if data.curbside is not None and len(data.curbside)
        else pd.DataFrame()
    )
    w = {
        site_id: model.addVar(vtype=gp.GRB.BINARY, name=f"w[{site_id}]")
        for site_id in curbside.index
    }
    f = {
        pair_index: model.addVar(vtype=gp.GRB.CONTINUOUS, lb=0.0, name=f"f[{pair_index}]")
        for pair_index in pairs.index
    }
    model.update()

    flow_by_demand = pairs.groupby("demand_id").groups
    flow_by_site = pairs.groupby("site_id").groups

    investment_cost = gp.quicksum(
        float(municipal.at[site_id, "fixed_cost_usd"])
        * int(municipal.at[site_id, "first_time_install_indicator"])
        * y[site_id]
        + float(municipal.at[site_id, "port_cost_usd"]) * x[site_id]
        for site_id in municipal.index
    )
    if len(curbside):
        investment_cost = investment_cost + gp.quicksum(
            float(curbside.at[site_id, "site_cost_usd"]) * w[site_id] for site_id in curbside.index
        )
        max_sites = config.get("curbside_max_sites")
        if max_sites is not None:
            model.addConstr(
                gp.quicksum(w[site_id] for site_id in curbside.index) <= int(max_sites),
                name="curbside_site_limit",
            )
    model.addConstr(investment_cost <= float(config["budget_usd"]), name="capital_budget")

    for site_id in municipal.index:
        upper = int(municipal.at[site_id, "max_additional_ports"])
        model.addConstr(y[site_id] <= x[site_id], name=f"activation_lb[{site_id}]")
        model.addConstr(x[site_id] <= upper * y[site_id], name=f"activation_ub[{site_id}]")

    for demand_id in demand.index:
        pair_indices = flow_by_demand.get(demand_id, [])
        model.addConstr(
            gp.quicksum(f[int(k)] for k in pair_indices)
            <= float(demand.at[demand_id, "projected_demand_kwh"]),
            name=f"demand[{demand_id}]",
        )

    for site_id in sites.index:
        pair_indices = flow_by_site.get(site_id, [])
        capacity = float(sites.at[site_id, "existing_capacity_kwh"])
        if site_id in municipal.index:
            capacity += float(municipal.at[site_id, "added_port_capacity_kwh"]) * x[site_id]
        elif site_id in w:
            capacity += float(curbside.at[site_id, "site_capacity_kwh"]) * w[site_id]
        model.addConstr(
            gp.quicksum(f[int(k)] for k in pair_indices) <= capacity,
            name=f"capacity[{site_id}]",
        )

    equity_lambda = float(config["equity_lambda"])
    primary_objective = gp.quicksum(
        (
            1.0
            + equity_lambda
            * float(demand.at[pairs.at[k, "demand_id"], "equity_shortage_score"])
        )
        * f[int(k)]
        for k in pairs.index
    )
    model.setObjective(primary_objective, gp.GRB.MAXIMIZE)
    model.optimize()

    if model.SolCount == 0:
        raise RuntimeError(f"No candidate solution. Solver status: {_status_name(gp, model.Status)}")

    primary_value = float(primary_objective.getValue())
    primary_status = _status_name(gp, model.Status)
    primary_gap = float(model.MIPGap)
    primary_tolerance = max(1e-4, abs(primary_value) * 1e-7)
    model.addConstr(primary_objective >= primary_value - primary_tolerance, name="primary_optimum")
    model.setObjective(investment_cost, gp.GRB.MINIMIZE)
    model.optimize()
    if model.SolCount == 0:
        raise RuntimeError("The cost tie-break solve did not return a candidate solution")

    flow_values = pd.Series({int(k): float(f[int(k)].X) for k in pairs.index})
    pairs["flow_kwh"] = pairs.index.map(flow_values).astype(float)
    demand_served = pairs.groupby("demand_id")["flow_kwh"].sum()
    site_served = pairs.groupby("site_id")["flow_kwh"].sum()

    municipal_result = data.municipal.copy()
    municipal_result["selected"] = municipal_result["site_id"].map(
        {site_id: int(round(y[site_id].X)) for site_id in municipal.index}
    )
    municipal_result["additional_ports"] = municipal_result["site_id"].map(
        {site_id: int(round(x[site_id].X)) for site_id in municipal.index}
    )
    municipal_result["investment_cost_usd"] = (
        municipal_result["fixed_cost_usd"]
        * municipal_result["first_time_install_indicator"]
        * municipal_result["selected"]
        + municipal_result["port_cost_usd"] * municipal_result["additional_ports"]
    )
    municipal_result["served_kwh"] = municipal_result["site_id"].map(site_served).fillna(0.0)

    demand_result = data.demand.copy()
    demand_result["served_kwh"] = demand_result["demand_id"].map(demand_served).fillna(0.0)
    demand_result["unmet_kwh"] = (
        demand_result["projected_demand_kwh"] - demand_result["served_kwh"]
    ).clip(lower=0.0)
    demand_result["service_rate"] = (
        demand_result["served_kwh"] / demand_result["projected_demand_kwh"]
    )

    curbside_result = None
    if len(curbside):
        curbside_result = data.curbside.copy()
        curbside_result["selected"] = curbside_result["site_id"].map(
            {site_id: int(round(w[site_id].X)) for site_id in curbside.index}
        )
        curbside_result["additional_ports"] = (
            curbside_result["selected"] * curbside_result["ports_per_site"]
        )
        curbside_result["investment_cost_usd"] = (
            curbside_result["selected"] * curbside_result["site_cost_usd"]
        )
        curbside_result["served_kwh"] = curbside_result["site_id"].map(site_served).fillna(0.0)

    site_result = data.sites.copy()
    added_ports_by_site = municipal_result.set_index("site_id")["additional_ports"]
    if curbside_result is not None:
        added_ports_by_site = pd.concat(
            [added_ports_by_site, curbside_result.set_index("site_id")["additional_ports"]]
        )
    site_result["additional_ports"] = site_result["site_id"].map(added_ports_by_site).fillna(0).astype(int)
    site_result["available_capacity_kwh"] = (
        site_result["existing_capacity_kwh"]
        + site_result["additional_ports"] * site_result["added_port_capacity_kwh"]
    )
    site_result["served_kwh"] = site_result["site_id"].map(site_served).fillna(0.0)
    site_result["utilization"] = site_result["served_kwh"] / site_result[
        "available_capacity_kwh"
    ].replace(0.0, pd.NA)

    municipal_spent = float(municipal_result["investment_cost_usd"].sum())
    curbside_spent = (
        float(curbside_result["investment_cost_usd"].sum()) if curbside_result is not None else 0.0
    )
    spent = municipal_spent + curbside_spent
    total_served = float(demand_result["served_kwh"].sum())
    weighted_served = float(
        (
            demand_result["served_kwh"]
            * (1.0 + equity_lambda * demand_result["equity_shortage_score"])
        ).sum()
    )
    summary = {
        "scenario_name": config["scenario_name"],
        "solver": "Gurobi",
        "solver_status": _status_name(gp, model.Status),
        "primary_solver_status": primary_status,
        "primary_mip_gap": primary_gap,
        "final_mip_gap": float(model.MIPGap),
        "primary_stage1_objective": primary_value,
        "primary_preservation_tolerance": primary_tolerance,
        "primary_objective_equity_weighted_kwh": weighted_served,
        "total_served_kwh": total_served,
        "baseline_demand_kwh": float(demand_result["baseline_demand_kwh"].sum()),
        "projected_demand_kwh": float(demand_result["projected_demand_kwh"].sum()),
        "unmet_projected_demand_kwh": float(demand_result["unmet_kwh"].sum()),
        "budget_usd": float(config["budget_usd"]),
        "investment_cost_usd": spent,
        "budget_slack_usd": float(config["budget_usd"]) - spent,
        "selected_municipal_sites": int(municipal_result["selected"].sum()),
        "additional_ports": int(municipal_result["additional_ports"].sum()),
        "demand_points": int(len(demand_result)),
        "supply_sites": int(len(site_result)),
        "accessible_pairs": int(len(pairs)),
        "equity_lambda": equity_lambda,
        "growth_multiplier": (1.0 + float(config["annual_demand_growth_rate"]))
        ** int(config["planning_horizon_years"]),
        "data_audit": data.audit,
        "note": "The second solve minimizes cost only among primary-objective-optimal solutions.",
    }
    if curbside_result is not None:
        selected_curb = curbside_result["selected"].eq(1)
        summary.update(
            {
                "municipal_investment_cost_usd": municipal_spent,
                "curbside_investment_cost_usd": curbside_spent,
                "curbside_candidates": int(len(curbside_result)),
                "selected_curbside_sites": int(selected_curb.sum()),
                "curbside_ports": int(curbside_result["additional_ports"].sum()),
                "served_by_curbside_kwh": float(curbside_result["served_kwh"].sum()),
                "served_by_municipal_kwh": float(municipal_result["served_kwh"].sum()),
                "service_rate": total_served
                / float(demand_result["projected_demand_kwh"].sum()),
                "selected_curbside_sites_by_county": (
                    curbside_result.loc[selected_curb, "county_name"].value_counts().to_dict()
                    if "county_name" in curbside_result
                    else {}
                ),
                "curbside_note": (
                    "additional_ports counts municipal ports only; curbside_ports is separate. "
                    "investment_cost_usd is the municipal + curbside total."
                ),
            }
        )

    tolerance = 1e-5
    max_demand_violation = float(
        (demand_result["served_kwh"] - demand_result["projected_demand_kwh"]).clip(lower=0).max()
    )
    max_capacity_violation = float(
        (site_result["served_kwh"] - site_result["available_capacity_kwh"]).clip(lower=0).max()
    )
    activation_ok = bool(
        (
            (municipal_result["selected"].eq(0) & municipal_result["additional_ports"].eq(0))
            | (
                municipal_result["selected"].eq(1)
                & municipal_result["additional_ports"].between(
                    1, municipal_result["max_additional_ports"]
                )
            )
        ).all()
    )
    selected_site_ids = set(municipal_result.loc[municipal_result["selected"].eq(1), "site_id"])
    if curbside_result is not None:
        selected_site_ids |= set(curbside_result.loc[curbside_result["selected"].eq(1), "site_id"])
        max_sites = config.get("curbside_max_sites")
        if max_sites is not None:
            activation_ok = activation_ok and int(curbside_result["selected"].sum()) <= int(max_sites)
    selected_with_access = selected_site_ids.issubset(set(pairs["site_id"]))
    checks = {
        "all_checks_pass": bool(
            spent <= float(config["budget_usd"]) + tolerance
            and max_demand_violation <= tolerance
            and max_capacity_violation <= tolerance
            and activation_ok
            and selected_with_access
            and pairs["distance_miles"].max() <= float(config["service_radius_miles"]) + tolerance
        ),
        "budget_feasible": spent <= float(config["budget_usd"]) + tolerance,
        "max_demand_violation_kwh": max_demand_violation,
        "max_capacity_violation_kwh": max_capacity_violation,
        "activation_constraints_hold": activation_ok,
        "selected_sites_have_accessible_demand": selected_with_access,
        "maximum_flow_pair_distance_miles": float(
            pairs.loc[pairs["flow_kwh"].gt(tolerance), "distance_miles"].max()
            if pairs["flow_kwh"].gt(tolerance).any()
            else 0.0
        ),
        "service_radius_miles": float(config["service_radius_miles"]),
        "weighted_objective_recomputed": weighted_served,
    }
    return Solution(summary, municipal_result, demand_result, site_result, checks, curbside_result)


def write_solution(solution: Solution, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "summary.json").open("w", encoding="utf-8") as stream:
        json.dump(solution.summary, stream, indent=2)
    with (output_dir / "sanity_checks.json").open("w", encoding="utf-8") as stream:
        json.dump(solution.sanity_checks, stream, indent=2)
    solution.municipal.sort_values(
        ["selected", "additional_ports", "facility_id"], ascending=[False, False, True]
    ).to_csv(output_dir / "municipal_candidate_solution.csv", index=False)
    demand_sort_column = "geography_id" if "geography_id" in solution.demand else "demand_id"
    solution.demand.sort_values(demand_sort_column).to_csv(
        output_dir / "demand_service_solution.csv", index=False
    )
    solution.site_utilization.sort_values("site_id").to_csv(
        output_dir / "site_utilization.csv", index=False
    )
    if solution.curbside is not None:
        solution.curbside.sort_values(
            ["selected", "served_kwh", "site_id"], ascending=[False, False, True]
        ).to_csv(output_dir / "curbside_candidate_solution.csv", index=False)
