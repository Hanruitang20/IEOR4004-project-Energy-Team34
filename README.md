# NYC Public Level 2 EV Charging Optimization

This repository contains the datasets used to build a capacitated location-allocation model for additional public Level 2 charging ports at eligible NYC DOT municipal parking facilities.

The model is intended to support code development for demand estimation, accessibility analysis, equity weighting, capacity constraints, investment decisions, and demand-growth scenarios.

## Repository structure

```text
data/       Source snapshots and prepared datasets
notebooks/  Exploratory analysis and model-development notebooks
src/        Reusable data preparation and optimization code
```

## Dataset inventory

| File | Contents | Records / sheets |
| --- | --- | --- |
| `NYC_EV_Project_Data.xlsx` | Consolidated project workbook, data guide, source notes, and prepared tables | 8 sheets |
| `NYC_Municipal_Parking_Locations.xlsx` | NYC DOT municipal parking facilities and reported parking/charging information | 46 worksheet rows |
| `dmv_electric_zip_summary_2026.csv` | Electric-vehicle registration records summarized by mailing ZIP | 404 rows |
| `nyc_public_operational_l2.csv` | Public, operational NYC stations with positive Level 2 port counts | 758 rows |
| `nyc_all_ev_stations.csv` | Broader NYC EV station inventory retained for review | 844 rows |
| `station_boundary_review.csv` | Stations near the NYC spatial boundary requiring manual review | 134 rows |
| `municipal_usage_monthly.csv` | Municipal charging sessions aggregated by location and month | 511 rows |
| `municipal_usage_status_counts.csv` | Session-status and invalidity-reason counts | 12 rows |
| `nyc_acs_vehicle_households_2020_2024.csv` | ACS vehicle availability by NYC census tract | 2,324 rows |
| `nyserda_nyc_plugin_snapshot_2023.csv` | Historical NYC BEV/PHEV registrations from the April 2023 NYSERDA snapshot | 401 rows |
| `icct_l2_hardware_2019.csv` | ICCT Level 2 charging-hardware cost benchmarks | 4 rows |
| `icct_l2_installation_2019.csv` | ICCT Level 2 installation cost benchmarks | 8 rows |

## Intended model use

- Baseline demand `D_i`: start with `dmv_electric_zip_summary_2026.csv` and document all energy-use and public-L2-share assumptions.
- Existing public L2 supply `C_j^0`: use `nyc_public_operational_l2.csv` with explicit assumptions for power, operating hours, availability, and shared power.
- Equity score `g_i`: compute accessible existing supply `S_i^0` from the EV-registration and public-L2 datasets before optimization.
- Candidate municipal facilities: use `NYC_Municipal_Parking_Locations.xlsx` and verify coordinates, reported spaces, existing ports, and electrical feasibility.
- Historical comparison: use `nyserda_nyc_plugin_snapshot_2023.csv` only after confirming that its vehicle definitions and geographic coverage are comparable with the 2026 DMV extract.
- Cost assumptions: use the two ICCT CSV files as 2019 benchmark inputs, not as current NYC project quotes.
- Municipal usage: use the monthly data as a plausibility check, not as unmet demand or an engineering capacity limit.

## Important limitations

- Mailing ZIP codes and Census ZCTAs are not identical geographic units.
- EV registration counts are not charging-energy demand. Demand requires documented conversion assumptions.
- Public stations may be accessible to more than one demand area. Accessible supply is therefore a proxy and not exclusive capacity for one ZIP.
- The historical 2023 NYSERDA snapshot and 2026 DMV extract should not be combined without a comparability review.
- Blank municipal inventory values mean unreported, not zero.
- ICCT costs are reported in 2019 USD and are not current NYC bids or quotes.
- Dataset dates and filters are documented in the `Data guide` and `Sources` sheets of `NYC_EV_Project_Data.xlsx`.

## Python setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Gurobi requires a separate valid license. Do not commit license files, access tokens, API keys, or local `.env` files.

## Data sources

The consolidated workbook records the source links, snapshot dates, filters, and limitations for AFDC/NYSERDA, NYS DMV, NYC Open Data, ACS, Census Gazetteer data, NYC borough boundaries, and ICCT cost benchmarks. Review the source terms before redistributing or publishing the repository.
