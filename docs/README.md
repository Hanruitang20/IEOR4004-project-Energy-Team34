# Project Documentation Index

Use this page to find the authoritative project documents. The current working result is the tract-level Gurobi model; the ZIP-point model is retained only as a comparison and sensitivity baseline.

## AI onboarding

- [AI Project Reading and Handoff Guide](../AGENTS.md): mandatory reading order, source-of-truth hierarchy, current model facts, change restrictions, and verification protocol for any AI assistant working from a local clone.

## Report documents

- [Milestone 3 Final PDF](../milestones/IEOR4004_Milestone3_Latest.pdf): finalized algebraic formulation that the code implements.
- [Milestone 4 Implementation and Results](../milestones/MILESTONE4.md): model-to-code mapping, tract data preparation, verified candidate solution, ZIP comparison, and sanity-check interpretation.
- [Milestone 5 Report Draft](../milestones/Milestone5_Draft.docx): current Word report draft (Section 6 updated November 18, 2026 with the resident-curbside sensitivity analysis).
- [Section 6 sensitivity run notes](../results/sensitivity_resident/RUN_NOTES.md): scenarios, solver settings, outputs and caveats.
- [Curbside Extension Scenario](CURBSIDE.md): optional curbside Level 2 candidates, formulation change, parameter sources, reference result and limitations. Does not change the base case.

## Execution document

- [Gurobi Run Instructions](../GUROBI_RUN_INSTRUCTIONS.md): setup, license check, exact tract command, expected output, tests, and output-file descriptions for the teammate running Gurobi.

## Supporting repository locations

- `config/tract_case.json`: current tract working-model assumptions.
- `config/base_case.json`: earlier ZIP-point comparison assumptions.
- `results/geography_comparison/tract/`: checked-in tract reference outputs.
- `results/geography_comparison/zip/`: checked-in ZIP reference outputs.
- `results/sensitivity/`: legacy ZIP sensitivity outputs.
- `data/`: source snapshots, prepared inputs, and source documentation workbook.

Return to the [project README](../README.md) for the current verified result and quick-start commands.
