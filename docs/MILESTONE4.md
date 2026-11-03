# Milestone 4 Implementation and Results

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
| Municipal sites `M` | 39 NYC DOT parking facilities after geocode-quality checks |
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
- Effective port capacity: 7.2 kW times 168 hours times 90% availability, or 1,088.64 kWh/week.
- First-time site cost: $20,000.
- Per-port cost: $6,217, equal to the documented $3,127 hardware and $3,090 installation benchmarks.
- Maximum additional ports: the smaller of 20 and 10% of remaining parking spaces after existing ports.
- Municipal/public-station match radius for deduplication: 0.05 mile.

The group must confirm the 5% growth rate, five-year horizon, equity weight of 1.0, 60 kWh/EV/week, and 25% public-L2 share before final submission. If any value changes, the model and all affected results must be rerun.

## Current tract result

For the assumptions above, Gurobi returned an optimal candidate solution with:

- 2,285 tract demand points.
- 786 modeled supply sites after municipal/public deduplication.
- 39 municipal investment candidates.
- 7,185 accessible tract-site pairs.
- 14 selected municipal facilities.
- 31 additional public Level 2 ports.
- $472,727 in modeled investment cost.
- 493,415.12 kWh/week of served demand.
- 982,519.84 kWh/week of projected demand.
- A projected-demand service rate of approximately 50.2%.
- An equity-weighted primary objective of approximately 519,139.52 weighted kWh/week.
- A maximum positive-flow distance of approximately 0.4998 mile.
- A final MIP gap of 0.0%.

All automated checks passed for the budget, projected-demand upper bounds, municipal and other-site capacities, activation and installation limits, accessibility, and maximum positive-flow distance.

`OPTIMAL` and a 0.0% MIP gap mean that Gurobi proved optimality for the implemented objective, constraints, data, and assumptions. They do not prove that the model perfectly represents future charging behavior or real-world construction feasibility.

## ZIP comparison and sanity check

The earlier ZIP-point version remains reproducible through `config/base_case.json`. It is a spatial baseline, not the current report result.

| Metric | ZIP baseline | Current tract model |
| --- | ---: | ---: |
| Demand points | 193 | 2,285 |
| Accessible pairs | 1,109 | 7,185 |
| Selected municipal sites | 9 | 14 |
| Additional ports | 44 | 31 |
| Investment cost | $453,548 | $472,727 |
| Served demand | 418,368.39 kWh/week | 493,415.12 kWh/week |
| Projected demand | 982,462.40 kWh/week | 982,519.84 kWh/week |
| Service rate | 42.6% | 50.2% |

The refined result is directionally plausible:

- Projected total demand remains nearly unchanged, so the tract allocation does not duplicate demand.
- Tract points spread demand within ZIP areas, allowing the model to use a wider set of nearby facilities.
- The tract solution selects more locations but fewer added ports per selected site, consistent with a less concentrated spatial representation.
- Both solutions respect the 0.5-mile base-case radius and pass the automated feasibility checks.

Do not compare the ZIP and tract equity-weighted objective values as if the weights were identical. The shortage score `g_i` is recomputed at the selected demand geography. Served energy, service rate, sites, ports, and cost are the more directly comparable metrics.

## Earlier sensitivity findings

The legacy ZIP sensitivity suite remains useful for diagnosing model behavior:

- Increasing the budget from $2.25 million to $5.25 million did not change the primary objective, showing that the budget was not binding in the 0.5-mile ZIP-point case.
- Increasing the radius to one mile raised served demand from about 418,368 to 709,156 kWh/week without a material spending increase, indicating that spatial accessibility mattered more than capital in that case.
- Setting `lambda = 0` preserved total served demand and selected investments but changed the allocation of 1,088.64 kWh/week from ZIP 11417 to ZIP 11416. The positive equity weight favored the ZIP with the higher baseline shortage score.
- Zero demand growth reduced added ports from 44 to 39, which is directionally consistent with lower projected demand.

These are diagnostic results from the ZIP representation. They should not be presented as reruns of the current tract model.

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
