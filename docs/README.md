# Documentation

## Start here

| Need | File |
| --- | --- |
| Run the current Gurobi model | [Step-by-step run guide](../GUROBI_RUN_INSTRUCTIONS.md) |
| Find the launcher | [run_gurobi.py](../run_gurobi.py) |
| Read Gurobi variables, objective and constraints | [src/optimization.py](../src/optimization.py) |
| Use Google Colab | [Current-model notebook](../notebooks/Run_Current_Model.ipynb) |
| Read the current formulation | [Resident-curbside model](RESIDENT_CURBSIDE_MODEL.md) |
| Understand cost parameters | [Cost assumptions](COST_PARAMETERS.md) |
| Understand operating hours and installation limits | [Input assumptions](INPUT_ASSUMPTIONS.md) |
| Understand resident-suggestion data | [Data provenance](RESIDENT_CURBSIDE_DATA.md) |
| Read sensitivity methods and recorded results | [Section 6 run notes](../results/sensitivity_resident/RUN_NOTES.md) |

## Reports and historical comparisons

- [Milestone 5 report snapshot](../milestones/Milestone5_Finalized.docx). This is the checked-in snapshot; it is not automatically synchronized with a live Google document.
- [Milestone 4 implementation](../milestones/MILESTONE4.md): parking-only tract baseline and ZIP comparisons.
- [Milestone 3 formulation](../milestones/IEOR4004_Milestone3_Latest.pdf): historical municipal-only formulation, extended by the current resident-curbside model.
- [Earlier synthetic curbside scenario](CURBSIDE.md): tract-center candidates, distinct from current resident-suggested locations.
- [Archived Milestone 4 notebook](../notebooks/archive/Milestone4_Parking_Only.ipynb): parking-only model; not the current model launcher.

Current results are in `results/resident_curbside_15m_cap150/`, with sensitivity cases in `results/sensitivity_resident/`. Older comparison outputs and original data are retained for reproducibility. [AGENTS.md](../AGENTS.md) gives the reading order and change rules for coding assistants.
