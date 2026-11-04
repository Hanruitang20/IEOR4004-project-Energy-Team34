# Milestone 4 Report Context and Reminders

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
- The operating-hours update used the cleaned workbook and revised coordinates. Its earlier results have been superseded by the current 20% installation-limit base case reported above. The implementation retains the nearest-station-per-facility matching algorithm. The older Gurobi notebook has not yet been updated to reflect the current model.
- **Unresolved inputs:** Bronxdale's 168 hours is labeled an assumption. Hunts Point's user-entered 168 hours is retained, although DOT's published Mon–Sat 6am–10pm totals 96. Gun Hill remains included at 112 hours, with a December 1, 2026 closure notice; this is not a claim of future access. Ferry overnight/Sunday access, courthouse garage versus outdoor-lot access, and Gowanus/Sunnyside curbside access need review. Do not describe these schedules as verified charging-access hours or model the announced closure as already applied.
- Equity scores are recalculated from existing hours-adjusted capacity before optimization. The five demand/policy inputs remain 60 kWh/EV/week, 25% public L2 share, 5% annual growth, five years and λ=1. Costs remain assumptions/historical benchmarks, distances remain point-based Haversine without barrier screening, and estimated tract locations do not locate individual EVs.

Run `python run_model.py --config config/tract_case.json --output-dir results/tract_case`, `python run_geography_comparison.py`, `python run_sensitivity.py`, and `python -m unittest discover -s tests` after changing hours. The sensitivity runner remains ZIP-based. `results/base_case` was also refreshed.


This document gives the team a shared reference for writing the Milestone 4 report. The current Milestone 3 formulation and working Gurobi model are frozen unless the group explicitly agrees to a change. Milestone 4 should explain the implementation faithfully rather than introduce a new model.

## 1. Formulation that should remain unchanged

### Primary objective

The implemented primary objective is

\[
\max \sum_{(i,j)\in A}(1+\lambda g_i)f_{ij}.
\]

This is algebraically equivalent to preserving the original total-demand-served term and adding the equity term:

\[
\max \left[
\sum_{(i,j)\in A}f_{ij}
+\lambda\sum_{(i,j)\in A}g_if_{ij}
\right].
\]

The report should not describe equity as replacing the original objective. When \(\lambda=0\), the model returns to the original unweighted objective.

### Projected demand constraint

The original demand upper bound was updated, not duplicated:

\[
\sum_{j:(i,j)\in A}f_{ij}
\le D_i(1+r)^T,
\qquad \forall i\in I.
\]

Do not include both \(\sum_j f_{ij}\le D_i\) and \(\sum_j f_{ij}\le D_i(1+r)^T\) in the same future-demand run. With positive growth, the original constraint would be more restrictive and would make the growth update ineffective.

### Other constraints

The remaining constraint groups retain the Milestone 3 logic:

1. Capital budget.
2. Investment activation and site installation limit.
3. Municipal-site capacity, including existing and added-port capacity.
4. Existing other-site capacity, with no investment at those sites.
5. Accessible-pair definition and variable domains.

For the municipal and other-site capacity constraints, flow must be summed over accessible demand points \(i\) for each fixed supply site \(j\).

## 2. Base-case assumptions used in the code

These are scenario assumptions and should not be presented as estimates obtained directly from the cross-sectional datasets.

- Capital budget: \(B=\$3{,}750{,}000\).
- Weekly energy per registered EV: 60 kWh.
- Public Level 2 charging share: 25%.
- Annual demand growth rate: \(r=5\%\).
- Planning horizon: \(T=5\) years.
- Service radius: \(R=0.5\) mile.
- Equity-policy weight: \(\lambda=1\).
- Port power: 7.2 kW.
- Availability factor: 90%.
- Municipal port capacity: 7.2 kW multiplied by facility-specific weekly operating hours and 90% availability. Capacity varies across municipal facilities.
- Other public Level 2 sites: 168 weekly operating hours are assumed, equivalent to 1,088.64 kWh/week per existing port.
- First-time installation cost: \$20,000 per selected site without existing public L2 ports.
- Incremental port cost: \$6,217 per added port.
- Maximum additional ports per municipal facility: the smaller of 20 ports and 20% of remaining parking spaces after existing Level 2 ports.
- Municipal/public-station matching radius for deduplication: 0.05 mile.

### Team confirmation required before final submission

The values \(r=5\%\), \(T=5\), and \(\lambda=1\) are inputs selected before optimization; they are not outputs calculated by Gurobi and are not estimates proven by the current cross-sectional datasets. The same applies to 60 kWh/EV/week and the 25% public-L2 charging share.

The current candidate solution was generated using all five of these base-case assumptions. Before the report is finalized, the team should explicitly confirm that it accepts:

1. 5% annual demand growth.
2. A five-year planning horizon.
3. An equity-policy weight of 1.0.
4. 60 kWh of weekly charging energy per registered EV.
5. A 25% public Level 2 charging share.

If the team accepts them, the report should state:

> For the first working base-case implementation, we set \(r=0.05\), \(T=5\), and \(\lambda=1.0\). Weekly energy use of 60 kWh per registered EV and a 25% public Level 2 charging share are also treated as scenario assumptions. These values are selected before optimization and are not claimed to be data-derived estimates.

If the group changes any of these assumptions, the Gurobi model must be rerun and every affected result, comparison, and sanity-check statement must be updated. The existing numerical results should not be reported under a different parameter set.

## 3. Demand geography used for Milestone 4

The refined working model uses Census tracts as demand points. The original ZIP-point model remains a sensitivity baseline.

The tract workflow is:

1. Begin with 2026 NYS DMV electric-registration records summarized by ZIP.
2. Use the official 2026 Q2 HUD-USPS ZIP-to-tract crosswalk.
3. Allocate each matched NYC ZIP total using the HUD residential-address ratio, normalized over matched NYC tracts because the input records represent NYC registrations.
4. Aggregate allocated registrations by tract.
5. Use each tract's Census internal point to construct tract-site pairs within 0.5 mile.

This procedure does not identify the location of any individual EV. The tract internal point is a spatial approximation.

## 4. Equity input used in the objective

The model uses charging-accessibility equity, not socioeconomic equity.

For each demand point, accessible existing capacity is

\[
S_i^0=\sum_{j:(i,j)\in A}C_j^0.
\]

The baseline charging-supply shortage score is

\[
g_i=\max\left(0,1-\frac{S_i^0}{D_i}\right)
\]

for \(D_i>0\), with \(g_i=0\) when \(D_i=0\).

The report must call \(g_i\) a supply-accessibility proxy. A charging site may be accessible to multiple demand points, so \(S_i^0\) is not exclusive capacity assigned to tract \(i\). The network capacity constraints prevent actual charging flow from using the same site capacity more than once.

The baseline \(g_i\) values are held fixed when demand-growth scenarios are compared. This avoids mixing the assumed future growth rate into the definition of current charging-resource shortage.

## 5. Gurobi implementation detail

The model is implemented as a mixed-integer linear program (MILP) using Gurobi.

The optimization follows a two-stage procedure:

**Stage 1: Maximize equity-weighted charging service**

The primary objective is:

Maximize Z = sum[(1 + lambda * g_i) * f_ij] over all accessible pairs (i,j).

The base case uses lambda = 1.0.

**Stage 2: Minimize investment cost**

After obtaining the optimal Stage 1 objective, the model constrains the equity-weighted objective to remain within a small numerical tolerance of its optimal value and minimizes total investment cost.

This second stage serves as a cost-minimizing tie-break. It avoids installing unnecessary charging ports while preserving near-optimal equity-weighted service. It does not replace the primary objective.

The current tract-level model contains:

- 2,285 Census tract demand points.
- 40 municipal investment candidates.
- 787 modeled supply sites.
- 7,191 accessible demand-site pairs.
- 40 binary site-selection variables.
- 40 integer added-port variables.
- 7,191 continuous charging-flow variables.

Both optimization stages returned OPTIMAL with a 0.0% MIP gap in the current base-case run.

## 6. Candidate solution to report

Under the current tract-level base case, using a $3.75 million budget, a 0.5-mile service radius, lambda = 1, 5% annual demand growth over five years, facility-specific municipal operating hours, and a 20% installation limit, Gurobi returned:

- 14 selected municipal facilities.
- 55 additional public Level 2 charging ports.
- $601,935 in modeled investment cost.
- 490,980.68 kWh/week of served demand.
- 982,519.84 kWh/week of projected demand.
- A projected-demand service rate of approximately 49.97%.
- A Stage 1 equity-weighted objective value of approximately 516,773.56.
- A maximum positive-flow distance of approximately 0.4998 mile.
- $3,148,065 of unused investment budget.
- Both optimization stages returning OPTIMAL with a 0.0% MIP gap.
- All automated feasibility checks passing.

The modeled investment cost uses a fixed first-time installation cost of $20,000 when applicable and an incremental cost of $6,217 per additional port.

The large unused budget does not necessarily indicate an optimization error. Under the current accessibility, demand, and capacity constraints, additional spending does not automatically increase the primary objective.

The solution should be described as a model-based candidate investment plan rather than a guaranteed real-world construction plan or an exact forecast of future charging activity.

## 7. Solver and result terminology

Use the following interpretations when describing the Gurobi output to readers who are not familiar with optimization terminology.

- **Solver status: OPTIMAL.** Gurobi found a feasible solution and proved that no better solution exists for the implemented objective, constraints, data, and assumptions. It does not prove that the assumptions perfectly represent the real world.
- **MIP gap.** The relative difference between the best feasible solution Gurobi has found and the best mathematical bound it has proved. A 0.0% final gap means the solver proved optimality for the implemented model. It is not a prediction-error measure or a data-quality measure.
- **Demand points.** The geographic units at which charging demand is represented. The tract case has 2,285 Census tract demand points; this does not mean there are only 2,285 EVs.
- **Accessible pairs.** Demand-point and supply-site combinations whose modeled distance is no greater than 0.5 mile. The current tract case has 7,191 accessible pairs. A pair indicates that service is allowed in the model, not that charging flow must be assigned to it.
- **Selected municipal sites.** Candidate NYC DOT facilities where the model chooses to install at least one additional public Level 2 port. The current tract result selects 14 of the 40 modeled candidates.
- **Additional ports.** The total number of new Level 2 charging ports installed across selected municipal sites. Existing ports are not included in this number.
- **Investment cost.** The modeled fixed first-time site costs plus incremental per-port costs for the selected investment. It is a planning estimate based on the stated assumptions, not a contractor bid.
- **Served demand.** Weekly charging energy allocated through the network flow variables, measured in kWh/week. It is limited by projected demand, site capacity, and accessibility.
- **Projected demand.** Baseline estimated public Level 2 demand multiplied by \((1+r)^T\). It is a scenario quantity, not a direct observation of future charging activity.
- **Service rate.** Total served demand divided by total projected demand. The current tract model achieves a service rate of approximately 49.97%. This represents the proportion of modeled weekly charging demand served, not necessarily the proportion of individual EV owners receiving service.
- **Maximum positive-flow distance.** The largest distance among accessible pairs that actually receive positive charging flow in the solution. The current tract value of approximately 0.4998 mile confirms that positive flows respect the 0.5-mile limit.
- **Sanity checks.** Automated tests that verify the returned solution respects the implemented budget, demand, capacity, activation, and distance rules. Passing checks confirms internal consistency, not real-world engineering feasibility.
- **Candidate solution.** The first working optimization result produced by the current model. It should not be described as a final construction plan.

## 8. Required sanity-check discussion
The report should explain why the current optimization results are internally consistent and economically reasonable.
The main sanity-check findings are:
- **ZIP versus tract comparison:** The ZIP-level model selected 10 municipal facilities and 88 additional ports, serving approximately 419,315.49 kWh/week at a modeled investment cost of $727,096. The Census-tract model selected 14 facilities and 55 additional ports, serving approximately 490,980.68 kWh/week at a cost of $601,935.
- **Demand conservation:** Total projected demand remains nearly unchanged between the ZIP and tract representations. This supports that the tract allocation procedure does not artificially duplicate charging demand.
- **Spatial resolution:** The tract-level model achieves a higher modeled service rate (49.97%) than the ZIP-level model (42.68%). This difference is primarily associated with the geographic representation of demand and the resulting accessibility relationships.
- **Budget feasibility:** The current tract-level solution spends $601,935 out of the $3.75 million available budget, leaving $3,148,065 unused. This does not indicate a budget constraint violation or an optimization error. Additional spending does not necessarily improve the objective under the current geographic and capacity constraints.
- **Accessibility:** The maximum positive-flow distance is approximately 0.4998 mile, consistent with the required 0.5-mile service radius. The current implementation uses Haversine distance and does not separately screen physical barriers.
- **Installation feasibility:** The current solution selects 14 of the 40 municipal candidate facilities and installs 55 additional ports. All selections satisfy the implemented 20% installation limit and the maximum of 20 additional ports per facility.
- **Solver verification:** Both optimization stages returned OPTIMAL with a 0.0% MIP gap, and all automated feasibility checks passed.
The ZIP-level sensitivity analysis also supports the importance of geographic accessibility. Increasing the service radius from 0.5 mile to 1.0 mile raised modeled served demand from approximately 419,315.49 to 712,538.78 kWh/week. However, the 0.5-mile radius remains the required base-case assumption.

These findings support the internal consistency of the implementation but do not establish that the modeled investment plan is an exact prediction of real-world charging behavior.

Equity-weighted objective values should not be directly compared between the ZIP and tract models because the shortage scores are recalculated for each demand geography.

## 9. Data-audit facts to disclose

- 51,322 matched electric-registration records were allocated to tracts.
- Allocated registration records equal matched source records exactly; the allocation conservation error is zero.
- Twenty-two ZIP rows containing 34 registration records had no positive residential-address match to an NYC tract and were not imputed.
- The 34 excluded records represent approximately 0.066% of the 51,356 positive NYC registration records.
- ZIPs with zero residential-address ratio remain in the data audit but are not assigned an invented residential coordinate.

## 10. Important limitations and wording cautions

### Barrier exclusions

Milestone 3 mentions documented barrier exclusions when defining accessible pairs. The current code implements the 0.5-mile Haversine-distance threshold but does not implement a separate bridge, water, highway, or pedestrian-barrier screen. The Milestone 4 report must not claim that barrier exclusions were executed in code.

Use wording such as:

> Accessible pairs in the current implementation are tract-site pairs whose Haversine distance is no greater than 0.5 mile. Additional physical-barrier screening remains a model refinement.

### Spatial precision

Residential-address ratios estimate how ZIP totals are distributed among tracts. They do not identify individual EV addresses or determine the exact distance from each EV to a charging site.

### Equity interpretation

The objective gives additional priority to areas with lower accessible existing charging capacity relative to baseline demand. It does not measure income equity, environmental justice, or guarantee equal service rates across all tracts.

### Demand and capacity assumptions

EV registrations are converted to weekly public L2 energy demand using assumed energy use and public-charging share. Port capacity is also an effective planning capacity based on assumed operating hours and availability. These are not engineering guarantees.

### Cost interpretation

The ICCT hardware and installation values are 2019 benchmarks, not current NYC bids or quotations. The \$3.75 million budget is a hypothetical planning scenario.

### Inventory wording

Do not state that every missing municipal charger count was independently verified as zero. Describe existing ports as based on reported municipal inventory and nearby public-station matching, and retain missing-inventory uncertainty as a limitation.

## 11. Recommended 3-5 page report structure

1. **Final formulation:** sets, parameters, decision variables, objective, and all constraints.
2. **Implementation and data preparation:** demand construction, tract allocation, supply capacity, candidate sites, costs, and accessible pairs.
3. **First Gurobi result:** solver status, selected sites, ports, cost, served demand, and service rate.
4. **Sanity checks:** feasibility checks and ZIP-versus-tract interpretation.
5. **Limitations and reproducibility:** assumptions, spatial approximation, unmatched ZIPs, barrier-screening limitation, and the GitHub link.

## 12. Reproduction commands

From the repository root:

```bash
.venv/bin/python run_model.py \
  --config config/tract_case.json \
  --output-dir results/tract_case

.venv/bin/python run_geography_comparison.py
.venv/bin/python -m unittest discover -s tests
```

Repository: <https://github.com/Hanruitang20/IEOR4004-project-Energy-Team34>

## 13. Items not to change without group agreement

- Do not replace the current equity objective with socioeconomic equity without adding and validating the required data.
- Do not change the 0.5-mile base radius without preserving it as the required base case.
- Do not introduce another demand-growth constraint in addition to the updated projected-demand constraint.
- Do not present assumed values as data-derived estimates.
- Do not replace the current model with a new dataset or forecasting framework before the Milestone 4 submission.
- Do not describe the candidate solution as a guaranteed real-world optimum outside the implemented model and assumptions.
