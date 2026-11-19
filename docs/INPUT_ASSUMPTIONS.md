# Operating Hours and Installation Limits

## Operating hours and capacity

The municipal source of truth is `data/NYC_Municipal_Parking_Locations.xlsx`, sheet `Facilities`, column `Scheduled hours/week`, joined by `Facility ID`. Geocoded CSVs supply locations, not replacement schedules.

For municipal facility j, `q_j = 7.2 × H_j × 0.90` kWh/(port·week) and `C_j^0 = n_j^0 × q_j`. Missing, nonnumeric, infinite, negative or greater-than-168 hours cause an error; zero is allowed. At 90 hours, each port contributes 583.2 kWh/week. Outputs retain the hours and review status.

Other existing public sites use an unverified 168-hour/week assumption. Selected curbside projects have four ports and capacity `4 × 7.2 × 168 × 0.60 = 2,903.04` kWh/week. Operating schedules, equipment availability and realized usage are different concepts; these formulas define planning capacity.

## Installation limits

All 40 municipal candidates use `U_j = min(20, floor(0.20 × max(0, parking spaces − existing L2 ports)))`. This is a space-allocation assumption, not a verified electrical or construction limit. There are no three-site exceptions. The current curbside cap is 150 **sites**, with four ports per selected site.

## Unresolved schedule inputs

- Bronxdale's 168 hours is an assumption.
- Hunts Point retains the user-entered 168 hours; DOT's published Mon–Sat 6am–10pm schedule totals 96 hours. This remains unresolved in the input snapshot.
- Gun Hill remains included at 112 hours, despite a December 1, 2026 closure notice. Inclusion is not a claim of future availability.
- Ferry overnight/Sunday access, courthouse garage versus outdoor-lot access, and Gowanus/Sunnyside charging access need review.

Scheduled parking hours are not necessarily verified charger-access hours. Changing hours or installation limits requires rerunning affected cases; do not compare new outputs with old assumptions without labeling the difference. Cost assumptions are documented in [COST_PARAMETERS.md](COST_PARAMETERS.md).
