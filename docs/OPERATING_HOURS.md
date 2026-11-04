# Site operating-hours parameter

## Current installation limits — November 4, 2026

All 40 municipal facilities now use the same planning rule: U_j = min(20, floor(0.20 × max(0, parking spaces_j − existing L2 ports_j))). This replaces the former 10% rule; no three-site exceptions are applied. Both tract and ZIP configurations use 20%. These are assumed space-allocation limits, not verified electrical or construction limits. Gun Hill remains included and its closure notice remains unresolved.

The refreshed tract base case selects 14 facilities and 55 additional ports for $601,935, serving 490,980.68 kWh/week out of 982,519.84 (49.97%). Both solve stages are OPTIMAL with 0.0% gaps. The radius remains 0.5 mile, λ=1, and the operating-hours capacity rule is unchanged. Compared with the previous 10% base case: +8 ports, +$49,736, and +4,665.60 kWh/week. These figures supersede earlier base-case results below.

The direct tract and ZIP cases, geography comparison, and five ZIP sensitivity cases were refreshed. All feasibility checks pass. The ZIP one-mile sensitivity cost solve retains a 0.393% gap under the configured 1% tolerance; do not label every sensitivity result an exact cost optimum. Nine pipeline tests pass. Earlier separately reported radius/growth experiments used the former 10% limits and are not current-base-case results.


## Operating-hours update — November 4, 2026

This update replaces the former uniform 168-hour municipal operating-time assumption with facility-specific weekly operating hours. The working demand geography remains Census tract; ZIP runs are comparison cases. The objective, projected demand, radius, cost rules and inventory-matching algorithm are unchanged.

- **H_j** is site operating hours in hours/week. Municipal values come from `data/NYC_Municipal_Parking_Locations.xlsx`, column `Scheduled hours/week`, joined by `Facility ID`. Excel is authoritative even if geocoded CSV metadata contains hours.
- **q_j = P × H_j × α**, and **C_j^0 = n_j^0 × P × H_j × α**, with P = 7.2 kW and α = 0.90. For 90 hours/week, q_j = 583.2 kWh/(port·week). Both municipal existing and added-port capacity use this rule. No new decision variable or constraint is needed.
- Missing, nonnumeric, infinite, negative or >168 municipal hours raise an error; zero is allowed. No municipal missing value silently becomes 168. Outputs expose `operating_hours_per_week` and its source/review status. Availability remains separate from scheduled hours.
- Other public sites retain the config `weekly_operating_hours` value of 168 as an **unverified assumption**. Municipal schedules must not be applied to unrelated private/curbside sites.
- The operating-hours update used the cleaned workbook and revised coordinates. Its earlier results have been superseded by the current 20% installation-limit base case: 14 selected facilities, 55 additional ports, $601,935 in investment cost, and 490,980.68 kWh/week served (49.97% of projected demand). The implementation retains its existing nearest-station-per-facility matching algorithm, and the updated Gurobi notebook now uses the current verified model pipeline.
- **Unresolved inputs:** Bronxdale's 168 hours is labeled an assumption. Hunts Point's user-entered 168 hours is retained, although DOT's published Mon–Sat 6am–10pm totals 96. Gun Hill remains included at 112 hours, with a December 1, 2026 closure notice; this is not a claim of future access. Ferry overnight/Sunday access, courthouse garage versus outdoor-lot access, and Gowanus/Sunnyside curbside access need review. Do not describe these schedules as verified charging-access hours or model the announced closure as already applied.
- Equity scores are recalculated from existing hours-adjusted capacity before optimization. The five demand/policy inputs remain 60 kWh/EV/week, 25% public L2 share, 5% annual growth, five years and λ=1. Costs remain assumptions/historical benchmarks, distances remain point-based Haversine without barrier screening, and estimated tract locations do not locate individual EVs.

Run `python run_model.py --config config/tract_case.json --output-dir results/tract_case`, `python run_geography_comparison.py`, `python run_sensitivity.py`, and `python -m unittest discover -s tests` after changing hours. The sensitivity runner remains ZIP-based. `results/base_case` was also refreshed.

