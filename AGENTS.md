# AI Project Reading and Handoff Guide

## Operating-hours update — November 4, 2026

This update supersedes earlier result figures and the uniform municipal 168-hour capacity assumption below. The working demand geography remains Census tract; ZIP runs are comparison cases. The objective, projected demand, radius, cost rules and inventory-matching algorithm are unchanged.

- **H_j** is site operating hours in hours/week. Municipal values come from `data/NYC_Municipal_Parking_Locations.xlsx`, column `Scheduled hours/week`, joined by `Facility ID`. Excel is authoritative even if geocoded CSV metadata contains hours.
- **q_j = P × H_j × α**, and **C_j^0 = n_j^0 × P × H_j × α**, with P = 7.2 kW and α = 0.90. For 90 hours/week, q_j = 583.2 kWh/(port·week). Both municipal existing and added-port capacity use this rule. No new decision variable or constraint is needed.
- Missing, nonnumeric, infinite, negative or >168 municipal hours raise an error; zero is allowed. No municipal missing value silently becomes 168. Outputs expose `operating_hours_per_week` and its source/review status. Availability remains separate from scheduled hours.
- Other public sites retain the config `weekly_operating_hours` value of 168 as an **unverified assumption**. Municipal schedules must not be applied to unrelated private/curbside sites.
- Current rerun: **2,285 demand points; 787 supply sites; 7,191 accessible pairs; 14 selected facilities; 47 added ports; $552,199 investment; 486,315.08 kWh/week served**, out of 982,519.84 projected (49.50%). Both stages return OPTIMAL and 0.0% gap. All nine refreshed tract, ZIP, comparison and ZIP-sensitivity runs pass feasibility checks; eight pipeline tests pass.
- These results use the cleaned workbook and revised coordinates. Changes from earlier outputs cannot be attributed to hours alone. The cloned repository uses its existing nearest-station-per-facility matching; the station-centric reconciliation described in earlier chat is not present in this checkout. This change does not silently replace that algorithm. Earlier notebooks are not revalidated by these pipeline runs.
- **Unresolved inputs:** Bronxdale's 168 hours is labeled an assumption. Hunts Point's user-entered 168 hours is retained, although DOT's published Mon–Sat 6am–10pm totals 96. Gun Hill remains included at 112 hours, with a December 1, 2026 closure notice; this is not a claim of future access. Ferry overnight/Sunday access, courthouse garage versus outdoor-lot access, and Gowanus/Sunnyside curbside access need review. Do not describe these schedules as verified charging-access hours or model the announced closure as already applied.
- Equity scores are recalculated from existing hours-adjusted capacity before optimization. The five demand/policy inputs remain 60 kWh/EV/week, 25% public L2 share, 5% annual growth, five years and λ=1. Costs remain assumptions/historical benchmarks, distances remain point-based Haversine without barrier screening, and estimated tract locations do not locate individual EVs.

Run `python run_model.py --config config/tract_case.json --output-dir results/tract_case`, `python run_geography_comparison.py`, `python run_sensitivity.py`, and `python -m unittest discover -s tests` after changing hours. The sensitivity runner remains ZIP-based. `results/base_case` was also refreshed.


This file applies to the entire repository. Any AI assistant working on this project must read the materials below in order before proposing edits, changing the model, or rewriting report content.

## Required reading order

1. Read `README.md` for the project scope, current verified result, repository map, and command overview.
2. Read `docs/IEOR4004_Milestone3_Latest.pdf` for the finalized algebraic formulation. Treat this PDF as the authority for the objective, sets, parameters, decision variables, and constraints.
3. Read `MILESTONE4_REPORT_REMINDERS.md` for the frozen interpretation, assumptions requiring group confirmation, terminology, limitations, and report wording.
4. Read `docs/MILESTONE4.md` for the model-to-code mapping, tract data preparation, current Gurobi result, ZIP comparison, and sanity-check interpretation.
5. Read `GUROBI_RUN_INSTRUCTIONS.md` before running or packaging the model.
6. Read `config/tract_case.json`, then `config/base_case.json`. The tract configuration is the current working model; the ZIP configuration is a comparison baseline.
7. Read the implementation in this order:
   - `src/data_preparation.py`
   - `src/optimization.py`
   - `run_model.py`
   - `run_geography_comparison.py`
   - `run_sensitivity.py`
   - `download_hud_crosswalk.py`
8. Read `tests/test_pipeline.py` to understand the automated invariants.
9. Inspect the checked-in result files in this order:
   - `results/geography_comparison/tract/summary.json`
   - `results/geography_comparison/tract/sanity_checks.json`
   - `results/geography_comparison/comparison.csv`
   - `results/geography_comparison/tract/municipal_candidate_solution.csv`
   - Other tract, ZIP, or sensitivity CSV files only as needed for the task.
10. Inspect `data/hud_zip_tract_crosswalk_metadata.json` and the `Data guide` and `Sources` sheets in `data/NYC_EV_Project_Data.xlsx` before making claims about data provenance.

## Source-of-truth hierarchy

Use the file that controls the type of claim:

1. Finalized Milestone 3 PDF for the mathematical formulation.
2. Code and tests for implementation behavior.
3. `config/tract_case.json` for current run assumptions.
4. Checked-in tract `summary.json` and `sanity_checks.json` for verified numerical results from the current committed run.
5. `MILESTONE4_REPORT_REMINDERS.md` for report interpretation and wording.
6. README and other summaries for navigation.

If these sources conflict, flag the conflict before editing or reporting a result. Do not silently reconcile it by inventing a value, changing the formulation, or overwriting checked-in results.

## Current model facts

- Current demand geography: Census tract.
- Required base-case service radius: 0.5 mile.
- Primary objective: maximize equity-weighted served demand using the finalized Milestone 3 formulation.
- Projected-demand limit: `D_i(1+r)^T`; do not add the old unprojected demand constraint to the same future-demand run.
- Current scenario inputs: `r=5%`, `T=5`, `lambda=1`, 60 kWh/EV/week, and 25% public-L2 share.
- These five inputs are assumptions requiring group confirmation; they are not values estimated by Gurobi.
- Current verified solution: 2,285 demand points, 7,185 accessible pairs, 14 selected municipal sites, 31 additional ports, $472,727 cost, and 493,415.12 kWh/week served.
- Solver status: `OPTIMAL`; final MIP gap: 0.0%; all automated checks pass.
- The ZIP-point model is a comparison baseline, not the current report result.

## Rules for changes

- Do not change the objective, constraints, symbols, 0.5-mile base case, or five highlighted scenario assumptions without explicit group approval.
- Do not present assumptions as data-derived estimates.
- Do not invent coordinates or impute unmatched ZIP records unless the group approves and the method is documented.
- Do not claim that bridge, water, highway, or pedestrian-barrier screening is implemented; the current accessible-pair code uses Haversine distance only.
- Do not describe the solution as a final construction plan or real-world guarantee.
- Preserve repository-relative paths. Never add a teammate's local absolute path.
- Never commit license files, HUD tokens, passwords, API keys, `.env` files, or machine-specific settings.
- Preserve the original data snapshots and checked-in reference results unless the task explicitly requires refreshing them.
- If an assumption, data-preparation rule, or model equation changes, rerun the affected model and update the results, README, implementation document, reminder, and tests together.

## Required verification

For documentation-only work:

```bash
git diff --check
python -m unittest discover -s tests
```

For model, configuration, or data-preparation changes:

```bash
python run_model.py --config config/tract_case.json --output-dir results/tract_case
python run_geography_comparison.py
python -m unittest discover -s tests
```

Confirm solver status, MIP gap, all sanity checks, record-allocation conservation, and maximum positive-flow distance before updating reported numbers.

## AI handoff response

After completing the reading sequence and before making a substantive change, summarize:

1. The current tract model and how the ZIP baseline is used.
2. The objective and projected-demand constraint in plain language.
3. The five assumptions requiring group confirmation.
4. The current verified candidate solution.
5. The important spatial, barrier-screening, equity, cost, and data limitations.
6. The exact files that the requested task would change and which verification commands will be run.

If the user's request is only to understand the repository, stop after this summary and do not modify files.
