# NYC Public Level 2 EV Charging Optimization

IEOR 4004, Team 34: Hanrui Tang, Jianing Lu, Yizhuo Yang and Selena Shen.

This Python/Gurobi project helps NYC DOT choose where to add public Level 2 charging at **40 municipal parking facilities** and **487 screened resident-suggested curbside locations**. Existing public chargers also serve demand but receive no investment. New parking construction and DC fast charging are outside the scope.

The model first maximizes equity-weighted weekly charging energy served, then minimizes installation cost while preserving the first-stage incumbent within a small numerical tolerance. Equity weights represent existing charging-access shortages, not income or demographic equity.

## How to run Gurobi

**Start with [run_gurobi.py](run_gurobi.py)**. It selects the current municipal + resident-curbside model. The actual Gurobi variables, objective and constraints are in [src/optimization.py](src/optimization.py).

1. Download and unzip the repository, or clone it. Open the project folder in desktop VS Code and open its terminal.
2. Activate Python 3.11+ with a suitable Gurobi license, then install the packages.
3. Run the launcher and open `outputs/current_model/` to see your results.

```bash
python -m pip install -r requirements.txt
python run_gurobi.py
python -m unittest discover -s tests
```

For environment setup, licensing, parameter changes and result interpretation, follow the **[step-by-step Gurobi run guide](GUROBI_RUN_INSTRUCTIONS.md)**. For Google Colab, open **[Run_Current_Model.ipynb](notebooks/Run_Current_Model.ipynb)** and run its cells in order.

The launcher uses `config/tract_resident_curbside_15m_cap150.json`; fresh results go to the Git-ignored `outputs/current_model/` folder. Use `--output-dir outputs/my_run` to keep another run. Reusing an output folder replaces its files. No original data or recorded reference results are changed by the default command. The main inputs and cached geocodes are included; normal execution does not download new data.

## Scenario and reference results

The current scenario uses a **hypothetical $15 million installation budget**, a **0.5-mile Haversine radius**, and a maximum of **150 new curbside sites**, each with four ports. Demand is represented by 2,285 Census-tract points, with 1,274 existing or candidate supply sites and 11,771 accessible demand-site pairs.

| Recorded result | Main reference | Section 6 sensitivity reference |
| --- | ---: | ---: |
| Demand served | 664,576.38 kWh/week (67.64%) | 665,451.47 kWh/week (67.73%) |
| Investment | $11,974,897 | $12,754,897 |
| Unused budget | $3,025,103 | $2,245,103 |
| Municipal facilities / added ports | 11 / 41 | 10 / 41 |
| New curbside sites / ports | 115 / 460 | 123 / 492 |
| MIP-gap setting / time per stage | 0.5% / 120 seconds | 0.01% / 600 seconds |
| Output folder | `results/resident_curbside_15m_cap150/` | `results/sensitivity_resident/reference/` |

These are **recorded candidate solutions**, not guaranteed identical outputs on every rerun. The main reference's Stage 1 and Stage 2 gaps are 0.2053% and 0.4672%; both returned OPTIMAL within the configured tolerance. Stage 2 preserves the Stage 1 incumbent rather than a proven exact maximum. Different incumbents and alternative site selections can affect the reported cost and site counts. Keep solver settings and result folders attached to reported numbers.

## Sensitivity analysis

```bash
python run_resident_sensitivity.py --include-radius
python plot_resident_sensitivity.py results/sensitivity_resident
```

This re-solves the reference and tests budget, curbside site cost, projected demand, curbside capacity factor, equity weight and service radius. It **replaces** the corresponding files in `results/sensitivity_resident/`; copy that folder first if you need to preserve the recorded runs. `python run_resident_sensitivity.py --summarize-only` rebuilds the comparison CSV without solving again.

Each scenario has its configuration and outputs in a separate subfolder. The combined results are in `sensitivity_comparison.csv`; charts are in `figures/`. Demand tests hold baseline shortage scores fixed. Radius tests recompute scores, while comparison service rates use the same reference high-shortage tract group.

The recorded `$125,000/site` scenario fails the strict post-solve capacity check by approximately 0.000022 kWh/week. Retain this numerical exception when reporting validation; do not label all recorded checks as passing.

## Inputs and assumptions

| Input | Current value or source |
| --- | --- |
| Demand | DMV ZIP registrations allocated to tracts using HUD residential-address ratios |
| Weekly public L2 demand | 60 kWh/EV/week × 25% public L2 share |
| Growth / equity weight | 5% annually for five years / λ = 1 |
| Existing supply | Public operational L2 inventory reconciled with municipal facilities |
| Municipal capacity | 7.2 kW × facility operating hours × 90% availability, per port |
| Curbside capacity | Four ports × 7.2 kW × 168 hours/week × 60% factor = 2,903.04 kWh/week per site |
| Municipal installation limit | Smaller of 20 ports and 20% of remaining parking spaces, rounded down |
| Municipal costs | $6,217/added port; $20,000 setup only at facilities with no modeled existing L2 ports |
| Curbside cost | $100,000 per four-port site |

Budgets, energy use, charging share, growth, power, capacity factors, costs and installation limits are planning assumptions or historical benchmarks—not confirmed NYC DOT allocations, construction quotes or verified electrical limits. Municipal hours come from the facility workbook; other public sites use an unverified 168-hour assumption. See [input assumptions](docs/INPUT_ASSUMPTIONS.md) for unresolved schedules, including Hunts Point and Gun Hill.

Resident pins are suggestions, not approved construction sites. Tract points approximate EV locations, and accessibility uses straight-line Haversine distance without street-network or barrier screening. The results do not establish construction feasibility or actual future utilization.

## Files and outputs

| Location | Purpose |
| --- | --- |
| `config/tract_resident_curbside_15m_cap150.json` | Current municipal + resident-curbside scenario |
| `src/data_preparation.py` | Demand allocation, inventory matching, capacities and accessibility |
| `run_gurobi.py` | Current-model launcher; start here |
| `src/optimization.py` | Actual Gurobi variables, constraints, two-stage objectives and checks |
| `notebooks/` | Current Colab runner and archived Milestone 4 notebook |
| `data/` | Cleaned workbooks, CSVs and source snapshots |
| `results/` | Recorded solutions, scenario comparisons and figures |
| `tests/` | Automated pipeline and model checks |

A run writes `summary.json`, `sanity_checks.json`, `municipal_candidate_solution.csv`, `curbside_candidate_solution.csv`, `demand_service_solution.csv` and `site_utilization.csv`. `additional_ports` in the summary counts municipal ports; `curbside_ports` is separate. Investment includes both.

For the complete navigation map, see [docs/README.md](docs/README.md). For detail, see [current formulation](docs/RESIDENT_CURBSIDE_MODEL.md), [cost parameters](docs/COST_PARAMETERS.md), [resident-data provenance](docs/RESIDENT_CURBSIDE_DATA.md) and [sensitivity run notes](results/sensitivity_resident/RUN_NOTES.md).

The parking-only tract model (`config/tract_case.json`) and ZIP model (`config/base_case.json`) are retained as comparison baselines. `run_geography_comparison.py` compares those baselines; `run_sensitivity.py` is the older ZIP sensitivity runner, not the current Section 6 analysis. Earlier synthetic tract-center curbside candidates are documented separately in [CURBSIDE.md](docs/CURBSIDE.md).
