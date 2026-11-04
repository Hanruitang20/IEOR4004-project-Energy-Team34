# Milestone 4 Implementation and Results

## Current installation limits — November 4, 2026

All 40 municipal facilities now use the same planning rule: U_j = min(20, floor(0.20 × max(0, parking spaces_j − existing L2 ports_j))). This replaces the former 10% rule; no three-site exceptions are applied. Both tract and ZIP configurations use 20%. These are assumed space-allocation limits, not verified electrical or construction limits. Gun Hill remains included and its closure notice remains unresolved.

The refreshed tract base case selects 14 facilities and 55 additional ports for $601,935, serving 490,980.68 kWh/week out of 982,519.84 (49.97%). Both solve stages are OPTIMAL with 0.0% gaps. The radius remains 0.5 mile, λ=1, and the operating-hours capacity rule is unchanged. Compared with the previous 10% base case: +8 ports, +$49,736, and +4,665.60 kWh/week. These are the current base-case results.

The direct tract and ZIP cases, geography comparison, and five ZIP sensitivity cases were refreshed. All feasibility checks pass. The ZIP one-mile sensitivity cost solve retains a 0.393% gap under the configured 1% tolerance; do not label every sensitivity result an exact cost optimum. Nine pipeline tests pass. Earlier separately reported radius/growth experiments used the former 10% limits and are not current-base-case results.


## Operating-hours update — November 4, 2026

This update replaces the former assumption of uniform 168-hour weekly operating time for municipal facilities with facility-specific operating hours. The working demand geography remains Census tract; ZIP runs are comparison cases. The objective, projected demand, radius, cost rules and inventory-matching algorithm are unchanged.

- **H_j** is site operating hours in hours/week. Municipal values come from `data/NYC_Municipal_Parking_Locations.xlsx`, column `Scheduled hours/week`, joined by `Facility ID`. Excel is authoritative even if geocoded CSV metadata contains hours.
- **q_j = P × H_j × α**, and **C_j^0 = n_j^0 × P × H_j × α**, with P = 7.2 kW and α = 0.90. For 90 hours/week, q_j = 583.2 kWh/(port·week). Both municipal existing and added-port capacity use this rule. No new decision variable or constraint is needed.
- Missing, nonnumeric, infinite, negative or >168 municipal hours raise an error; zero is allowed. No municipal missing value silently becomes 168. Outputs expose `operating_hours_per_week` and its source/review status. Availability remains separate from scheduled hours.
- Other public sites retain the config `weekly_operating_hours` value of 168 as an **unverified assumption**. Municipal schedules must not be applied to unrelated private/curbside sites.
- The operating-hours update used the cleaned workbook and revised coordinates. Its earlier results have been superseded by the current 20% installation-limit base case reported above. The implementation retains the nearest-station-per-facility matching algorithm. The Gurobi notebook now uses the current verified model pipeline.
- **Unresolved inputs:** Bronxdale's 168 hours is labeled an assumption. Hunts Point's user-entered 168 hours is retained, although DOT's published Mon–Sat 6am–10pm totals 96. Gun Hill remains included at 112 hours, with a December 1, 2026 closure notice; this is not a claim of future access. Ferry overnight/Sunday access, courthouse garage versus outdoor-lot access, and Gowanus/Sunnyside curbside access need review. Do not describe these schedules as verified charging-access hours or model the announced closure as already applied.
- Equity scores are recalculated from existing hours-adjusted capacity before optimization. The five demand/policy inputs remain 60 kWh/EV/week, 25% public L2 share, 5% annual growth, five years and λ=1. Costs remain assumptions/historical benchmarks, distances remain point-based Haversine without barrier screening, and estimated tract locations do not locate individual EVs.

Run `python run_model.py --config config/tract_case.json --output-dir results/tract_case`, `python run_geography_comparison.py`, `python run_sensitivity.py`, and `python -m unittest discover -s tests` after changing hours. The sensitivity runner remains ZIP-based. `results/base_case` was also refreshed.


The current Milestone 4 implementation converts the finalized Milestone 3 formulation into a working Gurobi model and produces a reproducible tract-level candidate solution. The original ZIP-point implementation is retained as a comparison case because it revealed the spatial-resolution issue addressed by the tract refinement.

## Execution sequence

1. Keep the Milestone 3 sets, parameters, variables, equity-weighted objective, and constraint groups unchanged.
2. Prepare tract demand, existing public Level 2 supply, municipal candidates, capacities, costs, fixed equity scores, and accessible pairs from repository-relative paths.
3. Solve the mixed-integer linear program with Gurobi.
4. Hold the optimal primary objective within a small numerical tolerance and minimize investment cost as a tie-break.
5. Export the candidate solution and run automated feasibility and comparison checks.

The tie-break removes unnecessary sites or ports among solutions with the same primary objective. It does not replace or modify the Milestone 3 objective.

## Model-to-code mapping

| Milestone 3 item | Current implementation |
| --- | --- |
| Demand points `I` | NYC Census tracts receiving allocated DMV electric-registration records through the HUD-USPS crosswalk |
| Municipal sites `M` | 40 eligible NYC DOT municipal parking facilities after geocode-quality checks |
| Other sites `O` | Public operational Level 2 station records after matching and removing municipal duplicates |
| Accessible pairs `A` | Tract-site pairs with Haversine distance no greater than 0.5 mile |
| `y_j`, `x_j`, `f_ij` | Gurobi binary, integer, and nonnegative continuous variables |
| Budget constraint | Fixed first-time cost plus per-port cost no greater than `B` |
| Activation constraint | `y_j <= x_j <= U_j y_j` |
| Projected demand | Flow to demand point `i` no greater than `D_i(1+r)^T` |
| Municipal capacity | Existing capacity plus per-port capacity times `x_j` |
| Other-site capacity | Existing capacity only |
| Objective | Maximize the sum of `(1 + lambda g_i) f_ij` |

The current code defines accessibility by distance only. It does not yet apply a separate bridge, water, highway, or pedestrian-barrier screen.

## Demand preparation

The tract workflow:

1. Begins with 2026 NYS DMV electric-registration records summarized by ZIP.
2. Uses the official 2026 Q2 HUD-USPS ZIP-to-tract crosswalk.
3. Normalizes each matched ZIP's positive residential-address ratios over NYC tracts because the source records represent NYC registrations.
4. Allocates the ZIP total across those tracts and aggregates the allocated records by tract.
5. Uses the ACS tract internal point to build tract-site pairs within 0.5 mile.

This procedure increases spatial detail but does not geolocate individual EVs. The HUD ratios estimate how a ZIP total is distributed, and the tract internal point remains an approximation for accessibility.

The data audit found that 51,322 matched registration records were conserved exactly. Twenty-two ZIP rows containing 34 records had no positive NYC tract match and were excluded rather than assigned invented coordinates. Those excluded records represent approximately 0.066% of the 51,356 positive NYC records.

## Scenario assumptions

These are selected inputs, not estimates calculated from the cross-sectional datasets or outputs produced by Gurobi.

- Budget: $3.75 million.
- Weekly energy per registered EV: 60 kWh.
- Public Level 2 share: 25%.
- Annual demand growth: 5% over five years.
- Equity-policy weight: `lambda = 1.0`.
- Service radius: 0.5 mile.
- Municipal port capacity: 7.2 kW multiplied by facility-specific weekly operating hours and 90% availability. Capacity varies across municipal facilities.
- Other public Level 2 sites: 168 weekly operating hours are assumed, equivalent to 1,088.64 kWh/week per existing port.
- First-time site cost: $20,000.
- Per-port cost: $6,217, equal to the documented $3,127 hardware and $3,090 installation benchmarks.
- Maximum additional ports per municipal facility: the smaller of 20 ports and 20% of remaining parking spaces after existing Level 2 ports.
- Municipal/public-station match radius for deduplication: 0.05 mile.

The group must confirm the 5% growth rate, five-year horizon, equity weight of 1.0, 60 kWh/EV/week, and 25% public-L2 share before final submission. If any value changes, the model and all affected results must be rerun.

## Current tract result

Under the current base-case assumptions, Gurobi returned the following optimal candidate solution:

- 2,285 Census tract demand points.
- 40 municipal investment candidates.
- 787 modeled supply sites.
- 7,191 accessible demand-site pairs.
- 14 selected municipal facilities.
- 55 additional public Level 2 charging ports.
- $601,935 in modeled investment cost.
- 490,980.68 kWh/week of served demand.
- 982,519.84 kWh/week of projected demand.
- A projected-demand service rate of approximately 49.97%.
- A Stage 1 equity-weighted objective value of approximately 516,773.56.
- $3,148,065 of unused investment budget.
- A maximum positive-flow distance of approximately 0.4998 mile.
- Both optimization stages returned OPTIMAL with a 0.0% MIP gap.

All automated feasibility checks passed for the budget, projected-demand upper bounds, site capacities, activation and installation limits, and accessibility requirements.

The result uses facility-specific municipal operating hours, a 20% installation limit, a 0.5-mile service radius, and an equity weight of lambda = 1.

The reported investment cost is based on the model's planning assumptions. Solver optimality confirms the best solution under the implemented model and assumptions, but does not guarantee real-world construction feasibility or future charging demand.

## ZIP comparison and sanity check

The ZIP-level model is retained as a spatial baseline for comparison with the current Census-tract model. Both scenarios use the same budget, demand assumptions, 0.5-mile radius, equity weight of lambda = 1, and 20% municipal installation limit.

| Metric | ZIP baseline | Current tract model |
| --- | ---: | ---: |
| Demand points | 193 | 2,285 |
| Accessible pairs | 1,110 | 7,191 |
| Selected municipal sites | 10 | 14 |
| Additional ports | 88 | 55 |
| Investment cost | $727,096 | $601,935 |
| Served demand | 419,315.49 kWh/week | 490,980.68 kWh/week |
| Projected demand | 982,462.40 kWh/week | 982,519.84 kWh/week |
| Service rate | 42.68% | 49.97% |

The tract-level model achieves a higher modeled service rate while requiring less investment than the ZIP-level baseline.

Projected total demand remains nearly unchanged, suggesting that the difference is mainly associated with the spatial representation of demand and the resulting accessibility relationships.

Both scenarios satisfy the implemented feasibility checks. However, the results remain dependent on the model assumptions and geographic approximations.

The equity shortage scores are recalculated for each demand geography. Therefore, equity-weighted objective values should not be directly compared across the ZIP and tract models.

## ZIP-level sensitivity findings

The ZIP-level sensitivity scenarios were rerun using the current 20% municipal installation limit. These experiments are diagnostic comparisons and should not be confused with the Census-tract base-case results.

The main findings are:

- Budget sensitivity: Increasing the budget from $2.25 million to $5.25 million did not change the selected investment plan or total served demand. Both scenarios selected 10 sites and 88 additional ports, with $727,096 in modeled investment cost and approximately 419,315.49 kWh/week served. This indicates that the budget is not binding over the tested range.

- Service radius: Increasing the service radius from 0.5 mile to 1.0 mile increased served demand from approximately 419,315.49 to 712,538.78 kWh/week. The modeled investment cost increased from $727,096 to $769,266. This suggests that geographic accessibility is a major limitation under the original 0.5-mile radius.

- Equity weighting: Setting lambda = 0 produced nearly the same total served demand and investment plan as lambda = 1 in the ZIP-level model. This does not imply that equity weighting has no effect on tract-level service allocation.

- Demand growth: Removing projected demand growth reduced the selected municipal facilities from 10 to 9 and additional ports from 88 to 76. Served demand decreased to approximately 342,748.53 kWh/week, consistent with lower projected demand.

All reported scenarios passed the implemented feasibility checks. The one-mile radius scenario's Stage 2 cost-minimization solve had a final MIP gap of approximately 0.393%, within the configured 1% tolerance, rather than an exact 0% gap.

These ZIP-level sensitivity results are separate from the Census-tract equity sensitivity experiments with lambda = 0, 1, 2, 4, and 10.

## Census-tract equity sensitivity analysis

To evaluate the effect of equity weighting, we tested five values of lambda: 0, 1, 2, 4, and 10. All scenarios used the same Census-tract demand data, 0.5-mile service radius, 20% municipal installation limit, facility-specific municipal operating hours, budget, and demand-growth assumptions.

| Equity weight | Selected sites | Additional ports | Investment cost | Served demand (kWh/week) |
| --- | ---: | ---: | ---: | ---: |
| 0 | 14 | 55 | $601,935 | 490,980.66 |
| 1 | 14 | 55 | $601,935 | 490,980.68 |
| 2 | 14 | 55 | $601,935 | 490,980.69 |
| 4 | 14 | 55 | $601,935 | 490,980.70 |
| 10 | 14 | 55 | $601,935 | 490,980.70 |

All five scenarios returned OPTIMAL with a 0.0% final MIP gap.

The number of selected facilities, number of additional ports, and total investment cost remained unchanged. Aggregate served demand also remained nearly constant across the tested equity weights.

However, the allocation of charging service across individual Census tracts changed.

Comparing lambda = 0 with lambda = 1:

- High-shortage tracts (g = 1): the aggregate service rate remained approximately 5.14%.
- Low-shortage tracts (g = 0): the aggregate service rate decreased from approximately 93.60% to 93.38%.
- Partial-shortage tracts (0 < g < 1): the aggregate service rate increased from approximately 24.43% to 30.54%.

These findings indicate that equity weighting can change how charging service is allocated without materially changing total service or modeled investment cost.

The improvement was concentrated in the small partial-shortage group, while the high-shortage group's aggregate service rate remained nearly unchanged. Therefore, the experiments do not establish that increasing lambda substantially improves access for the most underserved tracts.

The equity-weighted objective values should not be directly compared across lambda scenarios as a measure of equity improvement because changing lambda also changes the objective function itself.

Detailed results are saved in `results/tract_equity/`, including the five scenario summaries and `results/tract_equity/equity_five_scenario_comparison.csv`.

## Reproduction

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_model.py --config config/tract_case.json --output-dir results/tract_case
python run_geography_comparison.py
python -m unittest discover -s tests
```

The official HUD-USPS crosswalk is included in `data/`, so the optimization does not require internet access. The normal run reads cached municipal geocodes. Regenerating those geocodes with `python src/geocode_candidates.py` requires internet access and may produce different results if the geocoding service changes.

For the report-ready formulation, terminology, assumptions, and limitations, return to [Milestone 4 Report Context and Reminders](../MILESTONE4_REPORT_REMINDERS.md).
