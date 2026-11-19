# Project Guide for Coding Assistants

## Current scope

The current model adds public L2 ports at 40 municipal parking facilities and selects among 487 screened resident-suggested curbside locations. It uses 2,285 tract demand points, 747 other existing public sites, a hypothetical $15M installation budget, a 0.5-mile Haversine radius and a cap of 150 four-port curbside sites. New parking construction and DC fast charging are outside scope.

The model maximizes equity-weighted weekly served energy, then minimizes cost while preserving the achieved Stage 1 incumbent within epsilon. The projected-demand bound is `D_i(1+r)^T`; do not add a simultaneous baseline-demand cap. A nonzero MIP gap does not establish an exact optimum.

## Required reading order

1. `README.md` and `GUROBI_RUN_INSTRUCTIONS.md` for the current scenario and execution.
2. `docs/RESIDENT_CURBSIDE_MODEL.md`, `docs/COST_PARAMETERS.md`, `docs/INPUT_ASSUMPTIONS.md` and `docs/RESIDENT_CURBSIDE_DATA.md` for formulation, inputs and limitations.
3. `config/tract_resident_curbside_15m_cap150.json`, then the comparison configs `config/tract_case.json` and `config/base_case.json`.
4. `src/data_preparation.py`, `src/resident_candidates.py`, `src/optimization.py`, `run_model.py`, `run_gurobi.py` and `run_resident_sensitivity.py`.
5. Tests in `tests/`; current `results/resident_curbside_15m_cap150/summary.json` and `sanity_checks.json`; sensitivity configs, summaries, checks and `RUN_NOTES.md` as relevant.
6. For historical context, `milestones/IEOR4004_Milestone3_Latest.pdf`, `milestones/MILESTONE4.md`, `run_geography_comparison.py` and `run_sensitivity.py`. Milestone 3 is the historical municipal-only formulation; use the resident-curbside document for the approved extension.
7. Before provenance claims, inspect `data/hud_zip_tract_crosswalk_metadata.json` and the `Data guide` and `Sources` sheets in `data/NYC_EV_Project_Data.xlsx`.

## Sources of truth

- Code and tests control implementation behavior; the selected scenario JSON controls numerical assumptions.
- Current formulation: `docs/RESIDENT_CURBSIDE_MODEL.md`. Fixed municipal cost absorbs the former first-time indicator before optimization.
- Main recorded result: `results/resident_curbside_15m_cap150/`, solved at 0.5% tolerance and 120 seconds per stage.
- Section 6 recorded scenarios: `results/sensitivity_resident/`, solved at 0.01% tolerance and 600 seconds per stage. Keep their numbers separate from the main reference.
- Parking-only tract and ZIP results are comparisons, not the current principal result. The synthetic tract-center curbside case is also historical.

Flag conflicts rather than inventing values or silently overwriting a recorded result. Solver incumbents, nonzero tolerances and alternative portfolios can produce different site lists and costs on reruns. Do not attribute every site swap to a scenario parameter.

The main recorded result is 664,576.38 kWh/week served (67.64%), $11,974,897 invested, 11 municipal facilities with 41 added ports, and 115 curbside sites with 460 ports. Its Stage 1 and Stage 2 gaps are 0.2053% and 0.4672%; all main-run checks pass. It was reproduced on November 19 with Gurobi 13.0.3. See the README for the distinct recorded sensitivity reference.

## Input and interpretation rules

- Do not change the objective, constraints, base radius or five demand/policy assumptions without group authorization: 60 kWh/EV/week, 25% public L2 share, 5% annual growth, five years and lambda = 1. These are scenario inputs, not values estimated by Gurobi.
- Municipal hours come from the facility workbook, column `Scheduled hours/week`, joined by `Facility ID`. The geocoded CSV supplies coordinates. Missing or invalid hours fail rather than becoming 168; zero is allowed.
- Municipal capacity is `7.2 × H_j × 0.90` per port. Other existing sites retain the unverified 168-hour assumption. A curbside site provides four ports and 2,903.04 kWh/week under its 60% capacity factor.
- Municipal installation limits are uniformly `min(20, floor(0.20 × max(0, spaces − existing L2 ports)))`. They are planning assumptions, not verified engineering limits.
- Retain unresolved schedules and closure notices described in `docs/INPUT_ASSUMPTIONS.md`; Gun Hill stays included unless explicitly instructed otherwise. Do not quietly correct Hunts Point's retained 168 hours without documenting and rerunning the change.
- Tract points and HUD residential ratios approximate EV locations. Do not invent coordinates or impute unmatched registration rows without approval and documentation.
- Accessibility is Haversine distance only. Do not claim bridge, water, highway, street-network or pedestrian-barrier screening.
- Equity scores measure accessible-existing-supply shortage against baseline demand, not income or demographics. Existing supply may appear in several scores, while network capacity constraints prevent flow from being used twice. Demand-growth sensitivity holds scores fixed; radius changes recompute them.
- Costs and budgets are assumptions/historical benchmarks, not contractor quotes or a confirmed remaining grant balance. Resident pins are not approved construction sites. Unknown inventory needs review.
- Keep source snapshots and checked-in results unless refreshing them is explicitly requested. Use `outputs/` for fresh local runs. Record both solver gaps, conservation, positive-flow distance and each feasibility check before reporting results.
- The recorded $125k/site sensitivity fails the strict capacity check by about 2.2e-05 kWh; retain the exception unless a separate numerical validation is documented. Never silently relabel a failed check.
- Keep paths repository-relative. Never commit license files, tokens, passwords, `.env` files or machine-specific settings.

## Verification

For documentation and organization changes, run `git diff --check` and `python -m unittest discover -s tests`. For a launcher change, also run `python run_gurobi.py` to a fresh ignored output folder. For model/config/data changes, rerun affected scenarios, baselines and tests, then update their documentation together. Do not overwrite historical outputs merely to verify a refactor.

Before substantive edits, summarize the current model, historical comparisons, assumptions, verified result, limitations, planned file changes and validation commands for the user. A request only to understand the repository does not authorize changes.
