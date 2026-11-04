# IEOR 4004 NYC Public Level 2 EV Charging Optimization

## Current installation limits — November 4, 2026

All 40 municipal facilities now use the same planning rule: U_j = min(20, floor(0.20 × max(0, parking spaces_j − existing L2 ports_j))). This replaces the former 10% rule; no three-site exceptions are applied. Both tract and ZIP configurations use 20%. These are assumed space-allocation limits, not verified electrical or construction limits. Gun Hill remains included and its closure notice remains unresolved.

The refreshed tract base case selects 14 facilities and 55 additional ports for $601,935, serving 490,980.68 kWh/week out of 982,519.84 (49.97%). Both solve stages are OPTIMAL with 0.0% gaps. The radius remains 0.5 mile, λ=1, and the operating-hours capacity rule is unchanged. Compared with the previous 10% base case: +8 ports, +$49,736, and +4,665.60 kWh/week. These are the current base-case results.

The direct tract and ZIP cases, geography comparison, and five ZIP sensitivity cases were refreshed. All feasibility checks pass. The ZIP one-mile sensitivity cost solve retains a 0.393% gap under the configured 1% tolerance; do not label every sensitivity result an exact cost optimum. Nine pipeline tests pass. Earlier separately reported radius/growth experiments used the former 10% limits and are not current-base-case results.


## Operating-hours update — November 4, 2026

This update replaces the former assumption of 168 weekly operating hours for all municipal facilities with facility-specific operating hours. The working demand geography remains Census tract; ZIP runs are comparison cases. The objective, projected demand, radius, cost rules and inventory-matching algorithm are unchanged.

- **H_j** is site operating hours in hours/week. Municipal values come from `data/NYC_Municipal_Parking_Locations.xlsx`, column `Scheduled hours/week`, joined by `Facility ID`. Excel is authoritative even if geocoded CSV metadata contains hours.
- **q_j = P × H_j × α**, and **C_j^0 = n_j^0 × P × H_j × α**, with P = 7.2 kW and α = 0.90. For 90 hours/week, q_j = 583.2 kWh/(port·week). Both municipal existing and added-port capacity use this rule. No new decision variable or constraint is needed.
- Missing, nonnumeric, infinite, negative or >168 municipal hours raise an error; zero is allowed. No municipal missing value silently becomes 168. Outputs expose `operating_hours_per_week` and its source/review status. Availability remains separate from scheduled hours.
- Other public sites retain the config `weekly_operating_hours` value of 168 as an **unverified assumption**. Municipal schedules must not be applied to unrelated private/curbside sites.
- The operating-hours update used the cleaned workbook and revised coordinates. Its earlier results have been superseded by the current 20% installation-limit base case reported above. The implementation retains the nearest-station-per-facility matching algorithm. The Gurobi notebook now uses the current verified model pipeline.
- **Unresolved inputs:** Bronxdale's 168 hours is labeled an assumption. Hunts Point's user-entered 168 hours is retained, although DOT's published Mon–Sat 6am–10pm totals 96. Gun Hill remains included at 112 hours, with a December 1, 2026 closure notice; this is not a claim of future access. Ferry overnight/Sunday access, courthouse garage versus outdoor-lot access, and Gowanus/Sunnyside curbside access need review. Do not describe these schedules as verified charging-access hours or model the announced closure as already applied.
- Equity scores are recalculated from existing hours-adjusted capacity before optimization. The five demand/policy inputs remain 60 kWh/EV/week, 25% public L2 share, 5% annual growth, five years and λ=1. Costs remain assumptions/historical benchmarks, distances remain point-based Haversine without barrier screening, and estimated tract locations do not locate individual EVs.

Run `python run_model.py --config config/tract_case.json --output-dir results/tract_case`, `python run_geography_comparison.py`, `python run_sensitivity.py`, and `python -m unittest discover -s tests` after changing hours. The sensitivity runner remains ZIP-based. `results/base_case` was also refreshed.


This repository contains the data, Gurobi implementation, verified outputs, and report guidance for Team 34's NYC public Level 2 charging location-allocation project.

The current Milestone 4 working model represents demand at the Census-tract level, uses the required 0.5-mile base-case radius, and solves the Milestone 3 equity-weighted formulation without changing its objective or constraints. The earlier ZIP-point implementation is retained as a spatial baseline for sanity checking.

> **Writing the report?** Start with [Milestone 4 Report Context and Reminders](MILESTONE4_REPORT_REMINDERS.md). It records the frozen formulation, assumptions requiring team confirmation, verified result terminology, limitations, and wording cautions.


## Current checked-in tract result

The current working model uses Census tracts as demand points, with a 0.5-mile service radius and an equity weight of lambda = 1.

The latest verified Gurobi results are stored in `results/tract_case/summary.json` and `results/geography_comparison/tract/summary.json`.

The current tract-level model reports:

- 2,285 Census tract demand points.
- 40 municipal investment candidates.
- 787 modeled supply sites.
- 7,191 accessible demand-site pairs.
- 14 selected municipal facilities.
- 55 additional Level 2 charging ports.
- $601,935 in modeled investment cost.
- 490,980.68 kWh/week of served demand.
- 982,519.84 kWh/week of projected demand.
- An overall service rate of 49.97%.
- $3,148,065 of unused budget.
- A Stage 1 equity-weighted objective value of 516,773.56.
- A maximum positive-flow distance of approximately 0.4998 mile.
- Both optimization stages returned OPTIMAL with a 0.0% MIP gap.
- All automated feasibility checks passed.

The model uses a $3.75 million budget, a 0.5-mile service radius, and lambda = 1 as the base-case equity weight.

The current installation limit is 20% of remaining parking spaces, capped at 20 additional ports per municipal facility.

Municipal charging capacity uses facility-specific weekly operating hours. Other public Level 2 sites use an assumed 168 operating hours per week.

These results represent a model-based candidate investment plan under the stated assumptions, not a final construction plan.


## Start here

| Need | Document or command |
| --- | --- |
| Give an AI assistant the full project context | [AI Project Reading and Handoff Guide](AGENTS.md) |
| Write or review the Milestone 4 report | [Milestone 4 Report Context and Reminders](MILESTONE4_REPORT_REMINDERS.md) |
| Run the project on a teammate's Gurobi environment | [Gurobi Run Instructions](GUROBI_RUN_INSTRUCTIONS.md) |
| Read the implementation and sanity-check findings | [Milestone 4 Implementation and Results](docs/MILESTONE4.md) |
| Review the final algebraic formulation | [Milestone 3 Final PDF](docs/IEOR4004_Milestone3_Latest.pdf) |
| Browse all project documentation | [Documentation Index](docs/README.md) |
| Run the current tract model | `python run_model.py --config config/tract_case.json --output-dir results/tract_case` |
| Run the ZIP-versus-tract comparison | `python run_geography_comparison.py` |
| Run automated tests | `python -m unittest discover -s tests` |

After pulling the repository, a teammate can start an AI session in the repository root and use:

> Read `AGENTS.md` and follow its required reading order. Before changing anything, give me the six-part AI handoff summary requested at the end of that file.

## Repository structure

```text
README.md                         Project overview and current verified result
AGENTS.md                         Required reading order and rules for AI assistants
MILESTONE4_REPORT_REMINDERS.md    Shared report-writing context at the repository root
GUROBI_RUN_INSTRUCTIONS.md        Portable setup and execution instructions
config/                           ZIP baseline and tract working-model assumptions
data/                             Source snapshots and prepared datasets
docs/                             Formulation, implementation notes, and documentation index
notebooks/                        Space for exploratory analysis
results/                          Checked-in reference and sensitivity outputs
src/                              Data preparation and optimization modules
tests/                            Automated pipeline and feasibility tests
```

## Quick start

Python 3.10 or later is recommended. A valid Gurobi license must be available in the execution environment.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_model.py --config config/tract_case.json --output-dir results/tract_case
python -m unittest discover -s tests
```

On Windows PowerShell, use `.venv\Scripts\activate` to activate the optional environment and place the model command on one line. Do not commit Gurobi license files, HUD tokens, passwords, API keys, or local `.env` files.

The verified tract reference outputs are checked in under `results/geography_comparison/tract/`. A new direct run writes to the output directory supplied on the command line.

## Model scope

The implementation:

- Allocates ZIP-level DMV electric-registration totals to NYC Census tracts using the official HUD-USPS residential-address ratio.
- Converts allocated registrations to baseline public Level 2 energy demand using explicit scenario assumptions.
- Builds existing public charging capacity and eligible NYC DOT municipal investment candidates.
- Allows service only over tract-site pairs within the 0.5-mile Haversine-distance radius.
- Maximizes the Milestone 3 equity-weighted served-demand objective.
- Holds that optimum and minimizes investment cost as a tie-break, without replacing the primary objective.
- Exports candidate investments, demand service, site utilization, solver statistics, and automated sanity checks.

## Scenario assumptions

The current tract run uses:

- Capital budget: $3.75 million.
- Weekly energy per registered EV: 60 kWh.
- Public Level 2 share: 25%.
- Annual demand growth: 5%.
- Planning horizon: five years.
- Equity-policy weight: 1.0.
- Service radius: 0.5 mile.
- Municipal added-port capacity: 7.2 kW × facility-specific weekly operating hours × 90% availability. Capacity varies by municipal facility.
- Other public Level 2 sites: 168 operating hours/week are assumed, giving 1,088.64 kWh/week per existing port.
- Maximum additional ports per municipal facility: the smaller of 20 ports and 20% of remaining parking spaces after existing Level 2 ports.
- First-time site cost: $20,000.
- Incremental port cost: $6,217.

These values are selected scenario inputs, not estimates produced by Gurobi. The group must confirm the growth rate, planning horizon, equity weight, weekly energy use, and public-L2 share before final submission. If any assumption changes, rerun the model and update every affected result.

## Demand geography and comparison

The current working model uses Census tracts. The earlier ZIP-point model remains available through `config/base_case.json` solely as a reproducible spatial baseline.

The updated comparison between the ZIP-level baseline and the Census-tract model is shown below. Both models use the same policy assumptions, including a 0.5-mile service radius, lambda = 1, and the updated 20% municipal installation limit.

| Metric | ZIP baseline | Current tract model |
| --- | ---: | ---: |
| Demand points | 193 | 2,285 |
| Municipal candidates | 40 | 40 |
| Supply sites | 787 | 787 |
| Accessible pairs | 1,110 | 7,191 |
| Selected municipal sites | 10 | 14 |
| Additional ports | 88 | 55 |
| Investment cost | $727,096 | $601,935 |
| Served demand | 419,315.49 kWh/week | 490,980.68 kWh/week |
| Projected demand | 982,462.40 kWh/week | 982,519.84 kWh/week |
| Projected-demand service rate | 42.68% | 49.97% |

The tract model achieves a higher modeled service rate than the ZIP-level baseline while requiring lower investment cost. The projected total demand is nearly unchanged, suggesting that the difference mainly reflects the spatial representation of demand and the resulting accessibility relationships.

The equity shortage scores are recalculated for each demand geography. Therefore, equity-weighted objective values should not be compared directly across the ZIP and tract models.


## Dataset inventory

| File | Contents | Records or sheets |
| --- | --- | ---: |
| `NYC_EV_Project_Data.xlsx` | Consolidated workbook, data guide, source notes, and prepared tables | 8 sheets |
| `NYC_Municipal_Parking_Locations.xlsx` | NYC DOT municipal parking facilities and reported parking or charging information | 46 rows |
| `dmv_electric_zip_summary_2026.csv` | Electric-vehicle registration records summarized by mailing ZIP | 404 rows |
| `nyc_public_operational_l2.csv` | Public, operational NYC stations with positive Level 2 port counts | 758 rows |
| `nyc_all_ev_stations.csv` | Broader NYC EV station inventory retained for review | 844 rows |
| `station_boundary_review.csv` | Stations near the NYC spatial boundary requiring manual review | 134 rows |
| `municipal_usage_monthly.csv` | Municipal charging sessions aggregated by location and month | 511 rows |
| `municipal_usage_status_counts.csv` | Session-status and invalidity-reason counts | 12 rows |
| `nyc_acs_vehicle_households_2020_2024.csv` | ACS vehicle availability by NYC Census tract | 2,324 rows |
| `hud_zip_tract_crosswalk.csv` | Official 2026 Q2 HUD-USPS New York ZIP-to-tract residential-address ratios | 11,320 rows |
| `nyserda_nyc_plugin_snapshot_2023.csv` | Historical NYC BEV/PHEV registrations from the April 2023 NYSERDA snapshot | 401 rows |
| `icct_l2_hardware_2019.csv` | ICCT Level 2 charging-hardware cost benchmarks | 4 rows |
| `icct_l2_installation_2019.csv` | ICCT Level 2 installation cost benchmarks | 8 rows |

The consolidated workbook records source links, snapshot dates, filters, and dataset-specific limitations.

## Reproducible workflows

Run the current tract case:

```bash
python run_model.py \
  --config config/tract_case.json \
  --output-dir results/tract_case
```

Run the spatial comparison and legacy ZIP sensitivity suite:

```bash
python run_geography_comparison.py
python run_sensitivity.py
```

The official crosswalk is already included. To refresh it from HUD, create a free token through the [official HUD API page](https://www.huduser.gov/portal/dataset/uspszip-api.html), then run:

```bash
HUD_API_TOKEN=YOUR_TOKEN python download_hud_crosswalk.py
```

The token is sent only in the request header and is not saved by the script.

## Important limitations

- HUD residential-address ratios estimate how ZIP totals are distributed among tracts; they do not reveal individual EV locations.
- A Census tract internal point is an approximation for the 0.5-mile accessibility test.
- The current code uses Haversine distance and does not implement a separate bridge, water, highway, or pedestrian-barrier screen.
- EV registrations become energy demand only through the documented weekly-energy and public-charging-share assumptions.
- Existing accessible supply is an equity proxy, not capacity reserved exclusively for one tract.
- Port capacity, installation limits, and costs are planning assumptions, not engineering guarantees or contractor bids.
- The ICCT hardware and installation inputs are 2019 benchmarks.
- Twenty-two ZIP rows containing 34 registrations had no positive NYC tract match and were excluded rather than assigned invented locations; 51,322 matched records were conserved exactly.

For the required reporting language and interpretation of these limitations, use [Milestone 4 Report Context and Reminders](MILESTONE4_REPORT_REMINDERS.md).
