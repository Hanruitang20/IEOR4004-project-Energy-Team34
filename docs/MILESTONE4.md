# Milestone 4 implementation and first-run findings

## Execution sequence

1. Keep the Milestone 3 sets, parameters, variables, objective, and six constraint groups unchanged.
2. Prepare demand points, public Level 2 supply, municipal candidates, capacities, costs, equity scores, and accessible pairs from repository-relative paths.
3. Solve the mixed-integer linear program with Gurobi.
4. Hold the primary equity-weighted objective at its optimum and minimize investment cost as a tie-break. This prevents unused ports from appearing in an otherwise equivalent optimal solution; it does not replace the Milestone 3 objective.
5. Export the candidate solution and run feasibility and sensitivity checks.

## Model-to-code mapping

| Milestone 3 item | Implementation |
| --- | --- |
| Demand points `I` | NYC DMV ZIP rows with a valid NYC lookup and ZCTA internal point |
| Municipal sites `M` | 39 NYC DOT parking facilities after geocode-quality checks |
| Other sites `O` | Public operational Level 2 records after matching and removing municipal duplicates |
| Accessible pairs `A` | Haversine distance no greater than the scenario radius; base case is 0.5 mile |
| `y_j`, `x_j`, `f_ij` | Gurobi binary, integer, and nonnegative continuous variables |
| Budget constraint | Fixed first-time cost plus per-port cost no greater than `B` |
| Activation constraint | `y_j <= x_j <= U_j y_j` |
| Projected demand | Sum of flow to demand point `i` no greater than `D_i(1+r)^T` |
| Municipal capacity | Existing capacity plus per-port capacity times `x_j` |
| Other-site capacity | Existing capacity only |
| Objective | Maximize the sum of `(1 + lambda g_i) f_ij` |

## Base-case assumptions

These values are scenario assumptions, not estimates claimed to come from the cross-sectional datasets.

- Budget: $3.75 million.
- Weekly energy per registered EV: 60 kWh.
- Public Level 2 share: 25%.
- Annual demand growth: 5% over five years.
- Equity-policy weight: `lambda = 1.0`.
- Effective port capacity: 7.2 kW times 168 hours times 90% availability, or 1,088.64 kWh/week.
- First-time site cost: $20,000.
- Per-port cost: $6,217, equal to the documented $3,127 hardware and $3,090 installation benchmarks.
- Maximum additional ports: the smaller of 20 and 10% of remaining parking spaces after existing ports.
- Municipal/public station match radius for deduplication: 0.05 mile.

## First working result

Gurobi returned an optimal base-case solution with 9 selected municipal facilities and 44 added ports. The primary equity-weighted objective was approximately 477,256 weighted kWh/week, while total served demand was approximately 418,368 kWh/week. The cost-minimal primary-optimal solution used approximately $453,548 of the $3.75 million budget.

All automated checks passed: budget, demand, site capacity, activation, selected-site accessibility, and maximum flow distance. The largest positive-flow distance was approximately 0.497 mile, below the 0.5-mile base radius.

## Sanity-check interpretation

- Increasing the budget from $2.25 million to $5.25 million did not change the primary objective. The budget is not binding in the current 0.5-mile ZIP-point model.
- The model leaves substantial projected demand unserved because many ZIP representative points have neither an existing public station nor a municipal candidate within 0.5 mile.
- A one-mile sensitivity increased total served demand from about 418,368 to 709,156 kWh/week without increasing spending materially. This indicates that spatial representation and the service radius drive the first solution more strongly than the capital budget.
- Setting `lambda = 0` preserved total served demand and the selected investments but changed the allocation of 1,088.64 kWh/week from ZIP 11417 to ZIP 11416. The positive equity weight favored ZIP 11417 because its baseline shortage score was higher.
- Zero demand growth reduced the number of added ports from 44 to 39, which is directionally consistent with lower demand.

These findings do not prove that the model is final. They identify the main item to review before Milestone 5: whether one ZIP internal point and a 0.5-mile radius represent accessibility at an appropriate spatial resolution.

## Tract-level refinement started now

The repository now contains a second demand-preparation path for this refinement rather than postponing it. It uses the official HUD-USPS ZIP-to-tract residential-address ratio to distribute each ZIP's EV registration records among NYC Census tracts. The allocated tract total is then represented by the Census tract internal point in the same 0.5-mile accessibility calculation.

This is more spatially detailed than treating an entire ZIP as one point, but it is not vehicle-level geolocation. The method estimates how many records belong to each tract; it cannot determine whether a particular EV is within 0.5 mile of a station. A tract internal point can also differ from the actual locations of households inside the tract, so the result must be described as a tract-level approximation.

The original ZIP configuration remains unchanged as the base implementation. The tract case is in `config/tract_case.json`, the official-data downloader is `download_hud_crosswalk.py`, and `run_geography_comparison.py` produces a side-by-side sanity check. HUD requires a free API token; the code does not store it. ZIPs absent from the official crosswalk are reported and excluded rather than assigned an invented coordinate.

### 2026 Q2 tract comparison

The official 2026 Q2 HUD-USPS New York crosswalk produced 2,285 tract demand points and 7,185 accessible demand-site pairs. All automated checks passed, including the 0.5-mile limit; the largest positive-flow distance was approximately 0.4998 mile.

- Projected demand remained essentially unchanged: 982,520 kWh/week for the tract case versus 982,462 for the ZIP case. The small difference represents a net three additional DMV registration records that could be allocated through the tract crosswalk despite missing ZCTA coordinates.
- Served demand increased from approximately 418,368 to 493,415 kWh/week, raising the service rate from 42.6% to 50.2%.
- The candidate solution changed from 9 selected municipal sites and 44 added ports to 14 selected sites and 31 added ports. Investment cost increased modestly from $453,548 to $472,727.
- The wider site distribution with fewer ports per selected site is directionally plausible because tract points spread demand within each ZIP instead of concentrating it at one ZIP internal point.
- Twenty-two DMV ZIP rows with 34 registration records had no positive NYC tract match and were excluded rather than imputed. The 51,322 matched registration records were conserved exactly during allocation.

The equity-weighted objective values should not be compared as if they used an identical weighting system because the shortage score is recomputed at the selected demand geography. Total served energy and service rate are the more directly comparable metrics across the ZIP and tract representations.

## Reproduction

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_model.py
python run_sensitivity.py
HUD_API_TOKEN=YOUR_TOKEN python download_hud_crosswalk.py
python run_geography_comparison.py
python -m unittest discover -s tests
```

The normal optimization run reads the cached municipal geocodes. To regenerate them from the address source, run `python src/geocode_candidates.py`; that step requires internet access and may change if the geocoding service changes.
