# NYC Public Level 2 EV Charging Optimization

This repository contains the datasets used to build a capacitated location-allocation model for additional public Level 2 charging ports at eligible NYC DOT municipal parking facilities.

The model is intended to support code development for demand estimation, accessibility analysis, equity weighting, capacity constraints, investment decisions, and demand-growth scenarios.

## Repository structure

```text
data/       Source snapshots and prepared datasets
notebooks/  Exploratory analysis and model-development notebooks
src/        Reusable data preparation and optimization code
config/     Explicit scenario assumptions
docs/       Milestone 4 method and sanity-check interpretation
results/    Reproducible base-case and sensitivity outputs
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
| `hud_zip_tract_crosswalk.csv` | Official HUD-USPS ZIP-to-tract residential-address ratios | Generated after HUD token setup |
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
- HUD `RES_RATIO` allocates a ZIP total among tracts; it does not reveal any vehicle's address. The tract internal point remains an approximation for the 0.5-mile accessibility test.
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

## Milestone 4 first working model

The repository now contains a Gurobi implementation of the Milestone 3 capacitated location-allocation model. It reads all inputs with repository-relative paths and exports a candidate solution plus automated feasibility checks.

The finalized Milestone 3 formulation used by the implementation is saved as `docs/IEOR4004_Milestone3_Latest.pdf`.

```bash
python run_model.py
```

The base-case assumptions are stored in `config/base_case.json`. They are intentionally separated from values derived from the datasets. The current first run selects 9 municipal facilities and 44 additional ports. See `docs/MILESTONE4.md` for the model-to-code mapping, first results, sensitivity checks, and the main spatial-resolution issue identified by the sanity check.

Useful commands:

```bash
python run_sensitivity.py
python -m unittest discover -s tests
```

## Tract-level demand refinement

The original ZIP internal-point implementation remains the reproducible base case. A second configuration implements the spatial refinement identified by the Milestone 4 sanity check:

1. Allocate each NYC ZIP's EV registration records across NYC Census tracts using the official HUD-USPS ZIP-to-tract `RES_RATIO`.
2. Normalize a ZIP's positive ratios over matched NYC tracts because the DMV source rows used here represent NYC records.
3. Aggregate allocated records by tract and use the ACS tract internal point for the 0.5-mile accessibility test.
4. Leave ZIPs with no official crosswalk match unallocated and report them in the data audit; do not invent locations.

HUD requires a free API token. Create one through the [official HUD API page](https://www.huduser.gov/portal/dataset/uspszip-api.html), then run:

```bash
HUD_API_TOKEN=YOUR_TOKEN python download_hud_crosswalk.py
python run_model.py --config config/tract_case.json --output-dir results/tract_case
python run_geography_comparison.py
```

Omitting year and quarter asks HUD for its latest available quarterly file; the returned period is saved in the metadata JSON for reproducibility. The token is used only in the request header and is never saved. Do not put it in the repository. The comparison output keeps the ZIP and tract results side by side so the effect of the spatial change can be sanity-checked rather than silently replacing the working base model.

## Data sources

The consolidated workbook records the source links, snapshot dates, filters, and limitations for AFDC/NYSERDA, NYS DMV, NYC Open Data, ACS, Census Gazetteer data, NYC borough boundaries, and ICCT cost benchmarks. Review the source terms before redistributing or publishing the repository.
