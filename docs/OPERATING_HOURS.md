# Site operating-hours parameter

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

