# Project Documentation Index

Use this page to find the authoritative project documents. The current working result is the tract-level Gurobi model; the ZIP-point model is retained only as a comparison and sensitivity baseline.

## Report documents

- [Milestone 4 Report Context and Reminders](../MILESTONE4_REPORT_REMINDERS.md): shared writing context, frozen formulation, assumptions requiring team confirmation, solver terminology, verified result, and wording cautions. This file remains in the repository root so every group member can see it immediately.
- [Milestone 3 Final PDF](IEOR4004_Milestone3_Latest.pdf): finalized algebraic formulation that the code implements.
- [Milestone 4 Implementation and Results](MILESTONE4.md): model-to-code mapping, tract data preparation, verified candidate solution, ZIP comparison, and sanity-check interpretation.

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
