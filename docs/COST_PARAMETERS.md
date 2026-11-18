# Simplified cost parameters for parking plus curbside planning

This notation change preserves the existing municipal cost assumptions; it does not change the solver or publish a new run.

| Parameter | Definition | Planning value / basis |
| --- | --- | --- |
| B | Combined installation budget, dollars | $15,000,000 hypothetical scenario; not a verified available grant balance. |
| F_j, j in M | Fixed project cost incurred only if municipal facility j receives additional ports, dollars/site | Precompute $20,000 when modeled existing L2 count n_j^0 = 0; $0 when n_j^0 > 0. Assumption, not an observed site quotation. Unknown inventory must be reviewed before classification. |
| c_j, j in M | Incremental installed cost per additional municipal port, dollars/port | $6,217 historical benchmark-based assumption; excludes shared work already counted in F_j. |
| K_k, k in K | Total installation cost of one four-port curbside project, dollars/site | $100,000 = 4 × $25,000; unverified planning assumption including installation. No additional municipal F_j is charged to these sites. |
| L | Maximum selected curbside sites | 150 sites; each selected site has four ports. |

The former fixed indicator a_j is absorbed into F_j and need not appear as a separate model parameter. Equivalently, F_j here equals F_j(old) × a_j(old). Site-selection variable y_j still equals 1 whenever municipal facility j receives any additional ports, whether it previously had charging or not. It does not indicate existing inventory.

Let M be municipal candidates, K be screened resident-suggested curbside candidates, x_j the additional municipal port count, and w_k a binary decision to open a four-port curbside site. The budget constraint becomes:

$$\sum_{j\in M}(F_j y_j+c_j x_j)+\sum_{k\in K}K_k w_k\le B.$$

The curbside-site limit is:

$$\sum_{k\in K}w_k\le150.$$

Municipal activation remains y_j ≤ x_j ≤ U_j y_j. Stage 2 minimizes the same combined cost expression while preserving Stage 1's equity-weighted served-energy objective. Capacity, demand and accessibility constraints retain their roles, with curbside capacity added for selected projects. The radius remains 0.5 mile.

A zero fixed expansion cost is a simplifying assumption: incremental expansion work is carried in c_j. If site-specific shared upgrade costs become available, F_j may also be positive at an existing charging facility. The $20,000 and $100,000 values require sensitivity analysis and should not be presented as verified NYC DOT costs.
