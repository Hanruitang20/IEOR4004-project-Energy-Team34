# IEOR 4004 NYC Public Level 2 EV Charging Optimization

This repository contains the data, Gurobi implementation, verified outputs, and report guidance for Team 34's NYC public Level 2 charging location-allocation project.

The current Milestone 4 working model represents demand at the Census-tract level, uses the required 0.5-mile base-case radius, and solves the Milestone 3 equity-weighted formulation without changing its objective or constraints. The earlier ZIP-point implementation is retained as a spatial baseline for sanity checking.

> **Writing the report?** Start with [Milestone 4 Report Context and Reminders](MILESTONE4_REPORT_REMINDERS.md). It records the frozen formulation, assumptions requiring team confirmation, verified result terminology, limitations, and wording cautions.

## Current verified result

Using `config/tract_case.json`, Gurobi returned an optimal candidate solution with:

- 2,285 Census-tract demand points and 7,185 accessible demand-site pairs.
- 14 selected municipal facilities and 31 additional Level 2 ports.
- $472,727 in modeled investment cost.
- 493,415.12 kWh/week served out of 982,519.84 kWh/week projected demand, or approximately 50.2%.
- A maximum positive-flow distance of approximately 0.4998 mile.
- A final MIP gap of 0.0% and all automated feasibility checks passing.

These values are a first working candidate solution under the stated data and scenario assumptions, not a final construction plan or an exact forecast.

## Start here

| Need | Document or command |
| --- | --- |
| Write or review the Milestone 4 report | [Milestone 4 Report Context and Reminders](MILESTONE4_REPORT_REMINDERS.md) |
| Run the project on a teammate's Gurobi environment | [Gurobi Run Instructions](GUROBI_RUN_INSTRUCTIONS.md) |
| Read the implementation and sanity-check findings | [Milestone 4 Implementation and Results](docs/MILESTONE4.md) |
| Review the final algebraic formulation | [Milestone 3 Final PDF](docs/IEOR4004_Milestone3_Latest.pdf) |
| Browse all project documentation | [Documentation Index](docs/README.md) |
| Run the current tract model | `python run_model.py --config config/tract_case.json --output-dir results/tract_case` |
| Run the ZIP-versus-tract comparison | `python run_geography_comparison.py` |
| Run automated tests | `python -m unittest discover -s tests` |

## Repository structure

```text
README.md                         Project overview and current verified result
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
- Effective added-port capacity: 1,088.64 kWh/week.
- First-time site cost: $20,000.
- Incremental port cost: $6,217.

These values are selected scenario inputs, not estimates produced by Gurobi. The group must confirm the growth rate, planning horizon, equity weight, weekly energy use, and public-L2 share before final submission. If any assumption changes, rerun the model and update every affected result.

## Demand geography and comparison

The current working model uses Census tracts. The earlier ZIP-point model remains available through `config/base_case.json` solely as a reproducible spatial baseline.

The checked-in 2026 Q2 comparison shows:

| Metric | ZIP baseline | Current tract model |
| --- | ---: | ---: |
| Demand points | 193 | 2,285 |
| Accessible pairs | 1,109 | 7,185 |
| Selected municipal sites | 9 | 14 |
| Additional ports | 44 | 31 |
| Investment cost | $453,548 | $472,727 |
| Served demand | 418,368.39 kWh/week | 493,415.12 kWh/week |
| Projected-demand service rate | 42.6% | 50.2% |

Projected total demand is nearly unchanged. The change in service is primarily a spatial-resolution effect. Do not compare the two equity-weighted objective values as if their shortage weights were identical, because the equity score is recomputed at each demand geography.

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
