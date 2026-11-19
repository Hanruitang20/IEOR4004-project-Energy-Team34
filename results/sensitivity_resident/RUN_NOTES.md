# Section 6 sensitivity analysis: resident curbside + municipal parking

Run from the repository root:

```bash
python run_resident_sensitivity.py --include-radius   # all scenarios (radius is optional)
python run_resident_sensitivity.py --summarize-only   # rebuild sensitivity_comparison.csv
python plot_resident_sensitivity.py results/sensitivity_resident   # figures/
```

**Reference:** `config/tract_resident_curbside_15m_cap150.json` ($15M budget, 0.5-mile radius, $100,000 per four-port curbside site, 60% curbside capacity factor, 150-site cap, λ = 1, 5% growth for five years). Each scenario changes one input and re-optimizes both stages. Each folder holds that scenario's `config.json` and full outputs. The checked-in reference results in `results/resident_curbside_15m_cap150/` are not modified.

| Group | Values | Config key |
|---|---|---|
| Budget | $3.75M, $7.5M, $10M, (15M), $20M | `budget_usd` |
| Curbside cost per site | $50k, $75k, (100k), $125k, $150k | `curbside_cost_per_port_usd` = site cost / 4 |
| Projected demand | 80%, (100%), 120%, 150% | `projected_demand_multiplier` (new; g_i unchanged) |
| Curbside capacity factor | 40%, (60%), 80% | `curbside_availability_factor` |
| Equity weight | λ = 0, (1), 2, 5 | `equity_lambda` |
| Radius (optional) | 0.25, (0.5), 0.75, 1.0 mi | `service_radius_miles` (code recalculates g_i) |

High-shortage service is measured on the fixed set of 1,121 tracts with reference g_i = 1.

**Solver.** Gurobi, November 18, 2026. All runs use a 0.01% MIP gap and a 600 s limit per stage, tighter than the reference's 0.5%, because several scenario differences are smaller than 0.5%. Both stages of every run returned OPTIMAL with all gaps at or below 0.0099%. At 0.01%, the re-solved reference serves 665,451.47 kWh/week (67.73%) for $12,754,897 with 10 municipal facilities (41 ports) and 123 curbside sites (492 ports). The checked-in reference at 0.5% reports 664,576.38 kWh/week with 115 sites for $11,974,897. All feasibility checks pass except `curbside_cost_125k`, whose `max_capacity_violation_kwh` is 2.2e-05 against the code's absolute 1e-05 threshold: numerical rounding (about 8e-9 of the site capacity), not a model violation. Scenarios whose service differs by a few kWh/week (for example `budget_20m`, `curbside_cost_50k`, `curbside_cost_75k` vs `reference`) are within the 0.01% tolerance and represent essentially the same plan.

**Alternative optima.** Runs with identical or near-identical service (for example λ = 0, 1, 2, 5, or $15M vs $20M) can select 11–16 different curbside pins. Most swapped pins are within 0.2 mile of their replacements. Use `curbside_sites_*_vs_reference` columns with this in mind.

Key results are written up in Section 6 of the Milestone 5 draft.
