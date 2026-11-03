# Milestone 4 Report Context and Reminders

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
- Weekly operating time: 168 hours.
- Availability factor: 90%.
- Effective capacity per added port: 1,088.64 kWh/week.
- First-time installation cost: \$20,000 per selected site without existing public L2 ports.
- Incremental port cost: \$6,217 per added port.
- Maximum added ports at a site: the smaller of 20 ports and 10% of remaining parking spaces after existing ports.
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

Gurobi first maximizes the Milestone 3 equity-weighted objective. After obtaining that optimum, the code constrains the primary objective to remain within a very small tolerance of its optimal value and minimizes investment cost.

This second solve is a tie-break procedure. It removes unnecessary selected sites or ports among primary-objective-optimal solutions; it does not replace or modify the Milestone 3 primary objective.

The tract run contains:

- 2,285 tract demand points.
- 786 modeled supply sites after municipal/public deduplication.
- 39 municipal investment candidates.
- 7,185 accessible tract-site pairs.
- 39 binary site-selection variables.
- 39 integer added-port variables.
- 7,185 continuous charging-flow variables.

## 6. Candidate solution to report

For the tract base case using \(r=5\%\), \(T=5\), \(\lambda=1\), 60 kWh/EV/week, and a 25% public-L2 share, Gurobi returned an optimal candidate solution with:

- 14 selected municipal facilities.
- 31 additional public Level 2 ports.
- \$472,727 in modeled investment cost.
- 493,415.12 kWh/week of served demand.
- 982,519.84 kWh/week of projected demand.
- A projected-demand service rate of approximately 50.2%.
- An equity-weighted primary objective of approximately 519,139.52 weighted kWh/week.
- Maximum positive-flow distance of approximately 0.4998 mile.
- Approximately \$3.277 million of unused budget.
- All automated feasibility checks passing.

The solution should be described as a first working candidate solution, not a final construction plan or an exact prediction of future charging activity.

## 7. Solver and result terminology

Use the following interpretations when describing the Gurobi output to readers who are not familiar with optimization terminology.

- **Solver status: OPTIMAL.** Gurobi found a feasible solution and proved that no better solution exists for the implemented objective, constraints, data, and assumptions. It does not prove that the assumptions perfectly represent the real world.
- **MIP gap.** The relative difference between the best feasible solution Gurobi has found and the best mathematical bound it has proved. A 0.0% final gap means the solver proved optimality for the implemented model. It is not a prediction-error measure or a data-quality measure.
- **Demand points.** The geographic units at which charging demand is represented. The tract case has 2,285 Census tract demand points; this does not mean there are only 2,285 EVs.
- **Accessible pairs.** Demand-point and supply-site combinations whose modeled distance is no greater than 0.5 mile. The tract case has 7,185 such pairs. A pair indicates that service is allowed in the model, not that charging flow must be assigned to it.
- **Selected municipal sites.** Candidate NYC DOT facilities where the model chooses to install at least one additional public Level 2 port. The tract result selects 14 of the 39 modeled candidates.
- **Additional ports.** The total number of new Level 2 charging ports installed across selected municipal sites. Existing ports are not included in this number.
- **Investment cost.** The modeled fixed first-time site costs plus incremental per-port costs for the selected investment. It is a planning estimate based on the stated assumptions, not a contractor bid.
- **Served demand.** Weekly charging energy allocated through the network flow variables, measured in kWh/week. It is limited by projected demand, site capacity, and accessibility.
- **Projected demand.** Baseline estimated public Level 2 demand multiplied by \((1+r)^T\). It is a scenario quantity, not a direct observation of future charging activity.
- **Service rate.** Total served demand divided by total projected demand. A 50.2% service rate means the modeled network serves approximately half of the projected demand under the stated constraints; it does not mean half of individual EV owners will necessarily receive service.
- **Maximum positive-flow distance.** The largest distance among accessible pairs that actually receive positive charging flow in the solution. The tract value of approximately 0.4998 mile confirms that positive flows respect the 0.5-mile limit.
- **Sanity checks.** Automated tests that verify the returned solution respects the implemented budget, demand, capacity, activation, and distance rules. Passing checks confirms internal consistency, not real-world engineering feasibility.
- **Candidate solution.** The first working optimization result produced by the current model. It should not be described as a final construction plan.

## 8. Required sanity-check discussion

The report should explain why the result is directionally plausible.

- The tract model spreads demand within ZIP areas and therefore selects more locations with fewer added ports per selected site.
- The ZIP-point baseline selected 9 sites and 44 ports, served approximately 418,368 kWh/week, and cost \$453,548.
- The tract model selected 14 sites and 31 ports, served approximately 493,415 kWh/week, and cost \$472,727.
- Projected total demand is nearly unchanged between the two representations. The change in served demand is primarily a spatial-resolution effect rather than duplicated demand.
- Increasing the budget did not materially improve the objective in the original 0.5-mile ZIP sensitivity. Accessibility and spatial representation were more binding than capital.
- Zero demand growth reduced the number of added ports in the earlier sensitivity run, which is directionally consistent with lower projected demand.

Do not compare the ZIP and tract equity-weighted objective values as if they used identical weights. The shortage score \(g_i\) is recomputed when demand geography changes. Total served energy, service rate, sites, ports, and cost are more directly comparable across the two geographic representations.

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
