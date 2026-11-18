# Resident-location parking plus curbside model

This approved extension preserves the municipal baseline and adds screened resident-suggested curbside candidates. The finalized Milestone 3 model remains the source for the historical parking-only formulation. Use the following additions for the resident-data scenario.

## Sets, parameters and decisions

- I: 2,285 Census-tract demand points; M: 40 municipal investment candidates; O: 747 other existing supply sites.
- K: 487 eligible resident-suggested curbside locations. J = M ∪ O ∪ K, with distinct site IDs. A contains 11,771 demand/site pairs within 0.5 mile. K has no existing modeled capacity.
- B = $15M hypothetical installation budget. L = 150 maximum new curbside sites.
- F_j = $20,000 if modeled existing municipal L2 count is zero, otherwise $0. This absorbs former a_j. c_j = $6,217 per added municipal port.
- n^c = 4 ports per curbside project, K_k = $100,000 per project, Q_k = 4 × 7.2 × 168 × 0.60 = 2,903.04 kWh/week per project. These are planning assumptions.
- Existing D_i, g_i, C_j^0, q_j and U_j retain their baseline definitions. Demand growth remains 5% for five years, weekly energy 60 kWh/EV and public L2 share 25%; λ=1.
- x_j: integer added municipal ports; y_j: binary municipal investment; w_k: binary curbside project; f_ij: nonnegative weekly energy allocation for (i,j) in A.

## Equations

Stage 1 maximizes ∑_(i,j)∈A (1+λg_i) f_ij. Stage 2 minimizes ∑_j∈M(F_j y_j+c_j x_j)+∑_k∈K K_k w_k, holding the achieved Stage 1 value within ε=max(10^-4,10^-7|Z_stage1|). With nonzero solver gaps this preserves an incumbent, not a proven exact optimum.

Constraints:

1. Shared budget: ∑_j∈M(F_j y_j+c_j x_j)+∑_k∈K K_k w_k ≤ B.
2. Municipal activation: y_j ≤ x_j ≤ U_j y_j, for j∈M.
3. Curbside site limit: ∑_k∈K w_k ≤150. Opening a site installs four ports; the cap applies to sites only.
4. Projected demand: ∑_{j:(i,j)∈A} f_ij ≤ D_i(1+r)^T, for i∈I.
5. Municipal capacity: ∑_{i:(i,j)∈A} f_ij ≤ C_j^0+q_j x_j, for j∈M.
6. Other existing supply: ∑_{i:(i,j)∈A} f_ij ≤ C_j^0, for j∈O.
7. Curbside capacity: ∑_{i:(i,k)∈A} f_ik ≤ Q_k w_k, for k∈K.
8. f≥0 only on A; x integer nonnegative; y,w binary. Service radius is fixed at 0.5 mile.

Municipal q_j and C_j^0 use facility-specific operating hours. Existing-supply shortage scores are computed before adding curbside candidates. Feedback counts screen candidate locations; they do not replace estimated EV energy demand. Construction feasibility, barriers and dedicated spare capacity at nearby existing stations are unverified.

## Verification and results

See [run notes](../results/resident_curbside_15m_cap150/RUN_NOTES.md) for the command, solver gaps and output definitions. The verified run serves 67.64%, investing $11,974,897 in 41 municipal and 460 curbside ports. Original parking-only and synthetic-curbside results remain historical comparisons.
