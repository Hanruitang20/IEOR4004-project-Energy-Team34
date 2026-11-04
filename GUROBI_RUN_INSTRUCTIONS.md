# Gurobi Run Instructions for Milestone 4

This package contains the code, configuration, data, tests, documentation, and reference outputs required to reproduce the IEOR 4004 Milestone 4 candidate solution. All project paths are relative to the extracted package directory.

## 1. Requirements

- Python 3.10 or later is recommended.
- A working Gurobi installation and license must already be available in the execution environment.
- Internet access is not required for the optimization run because the official HUD-USPS crosswalk is included in `data/`.
- Do not place a Gurobi license file, HUD token, password, or `.env` file inside the project directory.

## 2. Extract and enter the package

Extract the ZIP file, open a terminal in the extracted folder, and confirm that the folder contains `run_model.py`, `config/`, `data/`, and `src/`.

## 3. Install the Python packages

If the Gurobi environment already provides Python and `gurobipy`, install only the remaining packages as needed:

```bash
python -m pip install -r requirements.txt
```

Creating a separate virtual environment is optional:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows, activate the optional environment with:

```powershell
.venv\Scripts\activate
```

## 4. Confirm that Gurobi is available

```bash
python -c "import gurobipy as gp; print('Gurobi version:', gp.gurobi.version())"
```

If this command reports a license error, the teammate operating the Gurobi environment must configure the academic, WLS, or institutional license outside the project directory before running the model.

## 5. Run the tract base case

```bash
python run_model.py \
  --config config/tract_case.json \
  --output-dir results/tract_case
```

For Windows PowerShell, use one line:

```powershell
python run_model.py --config config/tract_case.json --output-dir results/tract_case
```

The current verified run uses:

- Annual demand growth: 5%.
- Planning horizon: five years.
- Equity-policy weight: 1.0.
- Weekly energy per registered EV: 60 kWh.
- Public Level 2 share: 25%.
- Service radius: 0.5 mile.

These are scenario inputs selected before optimization, not values estimated by Gurobi.

## 6. Expected base-case result

A successful run using `config/tract_case.json` should reproduce the current checked-in tract-level reference result:

- 2,285 Census tract demand points.
- 40 municipal investment candidates.
- 787 modeled supply sites.
- 7,191 accessible demand-site pairs.
- 14 selected municipal facilities.
- 55 additional Level 2 charging ports.
- $601,935 in modeled investment cost.
- Approximately 490,980.68 kWh/week of served demand.
- 982,519.84 kWh/week of projected demand.
- An overall service rate of approximately 49.97%.
- $3,148,065 of unused investment budget.
- A Stage 1 equity-weighted objective value of approximately 516,773.56.
- Both optimization stages returning OPTIMAL with a 0.0% MIP gap.
- All automated feasibility checks passing.

These results use a $3.75 million budget, a 0.5-mile service radius, lambda = 1, facility-specific municipal operating hours, and the updated 20% installation limit.

Small numerical differences due to solver tolerances may be acceptable, but material differences in selected sites, ports, investment cost, or total served demand should be investigated before updating the report.

The reported results represent a model-based candidate solution under the stated assumptions, not a final construction plan.

## 7. Run the ZIP-versus-tract comparison

```bash
python run_geography_comparison.py
```

The comparison is written to:

```text
results/geography_comparison/comparison.csv
```

## 8. Run automated tests

```bash
python -m unittest discover -s tests
```

## 9. Output files

The tract run writes:

- `summary.json`: solver status, objective, demand, cost, and counts.
- `sanity_checks.json`: feasibility and distance checks.
- `municipal_candidate_solution.csv`: selected municipal facilities and added ports.
- `demand_service_solution.csv`: served and unmet demand by tract.
- `site_utilization.csv`: capacity and utilization by supply site.

## 10. Important reporting limitation

The current implementation defines accessible pairs using Haversine distance no greater than 0.5 mile. It does not implement a separate bridge, water, highway, or pedestrian-barrier screen. The report should not claim that barrier exclusions were executed in code.

For the full reporting context, assumptions, terminology, limitations, and interpretation, see [Milestone 4 Report Context and Reminders](MILESTONE4_REPORT_REMINDERS.md). The [Documentation Index](docs/README.md) links the remaining formulation and implementation documents.
