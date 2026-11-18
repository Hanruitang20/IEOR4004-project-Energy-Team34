# Curbside Level 2 Extension Scenario

This is an **optional extension scenario**. The base case (`config/tract_case.json`, `results/tract_case/`) is unchanged and remains the frozen Milestone 3/4 result. The curbside case adds one new set of candidate sites and keeps everything else from the tract base case.

## Why

In the tract base case, the municipal installation limits bind before the budget does: only $601,935 of the $3.75M budget is spent, and 1,121 of 2,285 tracts have no existing public L2 supply within 0.5 mile. Curbside chargers can add supply in those tracts.

## Formulation change (minimal)

New set: K = curbside candidates, one at the Census tract internal point of every tract with zero accessible existing supply (1,121 candidates).

New decision variable: w_k ∈ {0,1}. Opening candidate k installs a fixed block of n^c = 4 ports.

Changes to existing constraints:

- **Budget:** add Σ_k (F^c + n^c·c^c)·w_k to the left-hand side of the existing capital-budget constraint (shared $3.75M budget).
- **Capacity (new, same form as the municipal constraint):** Σ_{i:(i,k)∈A} f_ik ≤ n^c · P · H^c · α^c · w_k for every k ∈ K.
- **Accessible pairs:** curbside pairs use the same Haversine 0.5-mile radius.
- **Optional:** Σ_k w_k ≤ N_max (`curbside_max_sites`; null = no cap).

The objective, the projected-demand constraint, equity scores g_i, the municipal constraints and all five scenario assumptions are unchanged. Equity scores are computed from existing supply only, so they are identical with and without the extension (tested).

## Parameters (`config/tract_curbside_case.json`)

| Key | Value | Basis |
|---|---|---|
| `curbside_ports_per_site` | 4 | NYC DOT (Aug 2026 press release): each station has at least two posts with two charging points each |
| `curbside_cost_per_port_usd` | 25,000 | Planning assumption: $15M federal grant for 600 curbside chargers (Canary Media). The grant amount may not equal total installed cost |
| `curbside_fixed_cost_per_site_usd` | 0 | Assumption; cost is carried in the per-port value |
| `curbside_weekly_operating_hours` | 168 | Curbside spaces are on-street, 24/7 |
| `curbside_availability_factor` | 0.6 | ≈ 0.70 occupancy × 0.85 actively-charging share reported by NYC DOT for the existing 88 curbside points |
| `curbside_max_sites` | null | No program-scale cap in the reference run |
| `mip_gap` | 0.0001 | Tightened from 0.01: at 1% the solver can stop at a visibly worse plan (32 vs 33 sites) |

Sources:
- NYC DOT, "Expansion of Curbside Electric Vehicle Charging" (Aug 4, 2026): https://www.nyc.gov/html/dot/html/pr2026/expansion-of-curbside-electric-vehicle-charging.shtml
- Canary Media, "NYC looks to kick its curbside EV-charging plans into second gear": https://canarymedia.com/articles/ev-charging/nyc-looks-to-kick-its-curbside-ev-charging-plans-into-second-gear

## Reference result (`results/tract_curbside_case/`)

| | Tract base case | + Curbside |
|---|---|---|
| Municipal facilities / ports | 14 / 55 | 10 / 43 |
| Curbside sites / ports | — | 33 / 132 |
| Investment | $601,935 | $3,747,331 (slack $2,669) |
| Served (kWh/week) | 490,980.68 | 583,373.79 |
| Service rate | 49.97% | 59.38% |
| Served by curbside (kWh/week) | — | 95,800.32 (all 33 sites at full capacity) |

Selected curbside sites by county: Kings 14, Queens 14, Richmond 4, Bronx 1. Other optimal solutions can choose different tracts with the same objective value, so the exact site list may differ between solvers.

All sanity checks pass. **Solver note:** this reference result was generated with SciPy/HiGHS through a gurobipy-compatible shim because Gurobi was not available in the generating environment. The unchanged tract base case was reproduced exactly with the same shim (14 facilities, 55 ports, $601,935, 490,980.68 kWh/week). Rerun with Gurobi before reporting:

```bash
python run_model.py --config config/tract_curbside_case.json --output-dir results/tract_curbside_case
```

## Outputs

Same files as the base case, plus `curbside_candidate_solution.csv` (one row per candidate: `selected`, `additional_ports`, `investment_cost_usd`, `served_kwh`). In `summary.json`, `additional_ports` and `selected_municipal_sites` still count municipal sites only; see `selected_curbside_sites`, `curbside_ports`, `municipal_investment_cost_usd`, `curbside_investment_cost_usd`, `served_by_curbside_kwh` and `service_rate`. `investment_cost_usd` is the combined total.

## Limitations

- Candidate locations are tract internal points, not verified block faces. No check for hydrants, bus stops, no-parking zones or curb ownership.
- No grid-capacity screening (for example, the Con Edison hosting capacity map).
- Curbside cost and availability are planning assumptions, not engineering estimates.
- Existing curbside pilot ports are not separately identified in `nyc_public_operational_l2.csv`. Any that appear there are modeled as ordinary public sites.
- Haversine distance only; no barrier screening (same as the base case).
