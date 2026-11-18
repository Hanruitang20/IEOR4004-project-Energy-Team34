# Resident-suggested curbside plus municipal parking: verified run

Run from the repository root:

```bash
python run_model.py --config config/tract_resident_curbside_15m_cap150.json --output-dir results/resident_curbside_15m_cap150
```

Gurobi 13.0.3, November 18, 2026. Both stages returned OPTIMAL within the configured 0.5% relative MIP tolerance: Stage 1 gap 0.2053%, Stage 2 gap 0.4672%. These are candidate solutions within tolerance, not exact zero-gap optima. Stage 2 preserves the achieved Stage 1 incumbent within 0.08505262 weighted kWh/week.

- 487 screened resident-suggested candidate pins, 40 municipal candidates, 2,285 demand tracts.
- 1,274 modeled sites including unbuilt candidates; 11,771 accessible pairs.
- Fixed 0.5-mile Haversine radius; no adaptive radius or travel subsidy.
- Hypothetical installation budget $15,000,000; cap 150 curbside sites, not ports.
- 11 municipal facilities add 41 ports for $474,897.
- 115 curbside sites add 460 ports for $11,500,000.
- Combined cost $11,974,897; remaining budget $3,025,103.
- Served demand 664,576.38 / 982,519.84 kWh/week = 67.64%.
- All feasibility checks pass; maximum positive-flow distance 0.499982883 mile.
- 19 automated tests pass. Rechecked tract and ZIP baselines retain their prior numerical results.

`additional_ports` in summary.json counts municipal ports only; add `curbside_ports` for 501 total new ports. Candidate CSVs include unselected rows. Resident pins are not approved construction sites. Cost, utilization, demand and access assumptions are documented in docs/RESIDENT_CURBSIDE_DATA.md and docs/COST_PARAMETERS.md. The $100,000 curbside site cost is an assumption, not a DOT quotation.

The candidate-source SHA256 is computed from the actual checked-in CSV bytes. Newline normalization changes a file hash but does not change parsed coordinates or records. Earlier exploratory runs are not overwritten.
