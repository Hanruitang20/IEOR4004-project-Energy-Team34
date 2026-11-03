# AI Project Reading and Handoff Guide

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
