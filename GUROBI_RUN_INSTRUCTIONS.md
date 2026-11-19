# How to Run the Gurobi Model

The main file is **[run_gurobi.py](run_gurobi.py)**. It selects the current municipal-parking plus resident-curbside scenario and saves a fresh result to `outputs/current_model/`.

The Gurobi variables, objective and constraints are implemented in **[src/optimization.py](src/optimization.py)**. The launcher imports that implementation; it does not duplicate the mathematics.

## 1. Download and open the project

On GitHub, choose **Code → Download ZIP**, unzip it, and open the extracted folder in desktop VS Code. Open **Terminal → New Terminal**. The terminal should be in the folder containing `run_gurobi.py`, `config/`, `data/` and `src/`.

Alternatively, clone it:

```bash
git clone https://github.com/Hanruitang20/IEOR4004-project-Energy-Team34.git
cd IEOR4004-project-Energy-Team34
```

The browser editor at github.dev edits files but does not provide the local Python/Gurobi runtime needed by this project. Use desktop VS Code or the Colab option below.

## 2. Select Python and install packages

Use Python 3.11 or later. If your existing project environment is already configured:

```bash
conda activate ieor4004
python --version
python -m pip install -r requirements.txt
```

For a new Conda environment:

```bash
conda create -n ieor4004 python=3.11 pip
conda activate ieor4004
python -m pip install -r requirements.txt
```

Without Conda, a virtual environment is another option:

```bash
python -m venv .venv
```

Activate it with `source .venv/bin/activate` on macOS/Linux or `.venv\Scripts\Activate.ps1` in Windows PowerShell, then install the requirements. Keep using `python` from the activated environment; `python3` may point to a different installation on macOS.

## 3. Check the Gurobi license

Installing `gurobipy` does not provide an unrestricted license. Use an academic, institutional or WLS license valid for your runtime. Do not put credentials or license files in this repository.

```bash
python -c "import gurobipy as gp; print('Gurobi:', gp.gurobi.version()); m = gp.Model(); m.dispose()"
```

A license error or “model too large for size-limited license” means the runtime needs a suitable license before the full model can run. A successful empty-model check alone does not establish that a size-limited license supports this full model.

If macOS reports `invalid user locale`, use `LC_ALL=C python run_gurobi.py` in the next step.

## 4. Run the current model

```bash
python run_gurobi.py
```

This uses `config/tract_resident_curbside_15m_cap150.json`: a hypothetical $15M budget, 0.5-mile radius, and at most 150 four-port curbside sites. It solves two stages: maximize equity-weighted service, then minimize cost while preserving the first-stage incumbent within a small tolerance.

The terminal ends with solver status, selected municipal and curbside sites, added ports, energy served, investment, feasibility-check status and the output location. The default allows 120 seconds per stage at a 0.5% MIP-gap setting. A fresh solve may finish sooner.

Choose a different output folder to retain several runs:

```bash
python run_gurobi.py --output-dir outputs/my_run
```

Running again into the same output folder replaces that folder's result files. The default folder is ignored by Git, so local reruns do not alter the checked-in reference outputs.

## 5. Find and read your results

Open `outputs/current_model/` in VS Code or Finder/File Explorer:

| File | What to read |
| --- | --- |
| `summary.json` | Service, cost, selected-site counts, status and both solver gaps |
| `sanity_checks.json` | Budget, capacity, demand, activation and distance checks |
| `municipal_candidate_solution.csv` | Municipal locations, selected flag and added ports |
| `curbside_candidate_solution.csv` | Curbside locations, selected flag and four-port projects |
| `demand_service_solution.csv` | Served and unmet weekly demand by tract |
| `site_utilization.csv` | Available capacity and energy allocation by supply site |

In a candidate CSV, filter **`selected = 1`** to see investment decisions. Unselected rows are retained so the complete candidate set can be reviewed. In the summary, `additional_ports` means municipal ports; add `curbside_ports` for the combined total. `investment_cost_usd` already includes both.

The recorded main result is 664,576.38 kWh/week served (67.64%) for $11,974,897: 11 municipal facilities with 41 added ports and 115 curbside sites with 460 ports. It is stored in `results/resident_curbside_15m_cap150/`. Nonzero solver gaps and alternative portfolios mean a rerun need not select identical sites. Read the actual gaps and checks rather than assuming an exact optimum or guaranteed construction feasibility.

## 6. Run the automated checks

```bash
python -m unittest discover -s tests
```

The November 19 verification passed all 21 tests. A passing test suite does not replace the feasibility checks of your particular solution. If `all_checks_pass` is false, inspect the individual residuals and do not silently relabel it as passing.

## 7. Optional sensitivity analysis and graphs

```bash
python run_resident_sensitivity.py --include-radius
python plot_resident_sensitivity.py results/sensitivity_resident
```

These commands test budget, curbside cost, projected demand, capacity factor, equity weight and radius. They use a tighter 0.01% gap and 600 seconds per stage. The full set can take longer than the main run.

**These commands replace the corresponding recorded sensitivity outputs and figures.** Copy `results/sensitivity_resident/` first if you need to preserve that snapshot. Read results in `sensitivity_comparison.csv`, per-scenario folders, and `figures/`. To rebuild the comparison table without solving again, use `python run_resident_sensitivity.py --summarize-only`.

## Change parameters or run comparison cases

`python run_gurobi.py --help` lists supported flags. For example:

```bash
python run_gurobi.py --budget-usd 10000000 --output-dir outputs/budget_10m
```

For other inputs, copy the current JSON config, edit the copy, then pass `--config path/to/copy.json`. Keep assumptions and output folders with reported numbers. Increasing radius also changes the accessibility-based shortage scores.

The lower-level `run_model.py` supports every config, but its no-argument default remains the older ZIP model. Use `run_gurobi.py` for the current model. Explicit comparison commands are:

```bash
python run_model.py --config config/tract_case.json --output-dir outputs/parking_only
python run_model.py --config config/base_case.json --output-dir outputs/zip_baseline
```

## Google Colab option

Open **[Run_Current_Model.ipynb](notebooks/Run_Current_Model.ipynb)** in Google Colab and run the cells from top to bottom. The notebook clones this repository, installs dependencies, runs the same `run_gurobi.py` launcher, displays the results and downloads a ZIP. Colab requires a Gurobi license valid for that runtime; the notebook explains how to use Colab Secrets for WLS credentials.
