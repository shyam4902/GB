# Project Instructions

## Scope
- The root `GB` repository combines R Markdown analysis/data with two independently versioned Flask applications.
- `GB_roster_analyzer/` and `lineup_optimizer/` each contain their own `.git` repository; check the relevant nested repository before changing or committing files there.

## Tech Stack
- Python Flask applications using pandas/numpy; SQLite backs the roster analyzer.
- `lineup_optimizer` declares PuLP as a dependency, but the current `app.py` uses a greedy pandas selection loop rather than an active PuLP model.
- R Markdown workflows use packages including `dplyr`, `readr`, `knitr`, `kableExtra`, and `brms`.
- No project-wide Python version, test runner, linter, CI configuration, or R lockfile is defined.

## Project Structure
- `GB_roster_analyzer/app.py` — primary roster upload, historical-sales valuation, and results web app.
- `GB_roster_analyzer/templates/` — Jinja/HTML UI for the roster analyzer and placeholder optimizer page.
- `GB_roster_analyzer/gameblazers.db` — SQLite database; the app reads the `sales_history` table.
- `lineup_optimizer/app.py` — stateless Flask upload/result adapter; this is the file referenced by its `Procfile`.
- `lineup_optimizer/optimizer_core.py` — exact football lineup solver and roster/projection normalization boundary.
- `lineup_optimizer/newapp.py` — alternate/older optimizer implementation; production status is unclear.
- `Contest_Analyzer/GB_modeling.Rmd` — historical contest-tier analysis using Bayesian models.
- `Projections/GameBlazers.Rmd` — roster filtering and weekly projection calculations.
- `data/raw/` — exported roster CSV input; `data/processed/` — generated projection output.

## Build & Run
- Roster analyzer: `cd GB_roster_analyzer && python app.py` (development server, debug enabled; do not treat this as a production launch command).
- Lineup optimizer: `cd lineup_optimizer && python3 app.py` (uses `PORT`, default `5000`, and binds to `0.0.0.0`).
- Deployment entry point for the optimizer: `lineup_optimizer/Procfile` contains `web: python3 app.py`.
- R Markdown files are intended to be opened/knit in RStudio; their current input paths include `~/Downloads`, so no reproducible CLI command is configured.
- Install Python dependencies from the requirements file inside the application being run; do not mix the two Flask dependency sets.

## Code Style & Conventions
- Python uses snake_case functions/variables, Flask route decorators, direct imports, and pandas DataFrame transformations.
- Existing error handling is mostly local `try/except` with Flask `flash()` messages in the roster analyzer and plain string responses in the optimizer.
- Templates contain page-specific inline CSS/JavaScript and use dark/light theme toggles; preserve the established UI behavior when editing them.
- R code uses snake_case object names and pipeline-style data transformation.

## Testing
- Run the optimizer suite from `lineup_optimizer/` with `.venv/bin/python -m unittest discover -v`.
- `lineup_optimizer/Test.py` remains a scratch script, not the test runner.
- Keep `optimizer_core.py` stable during UI work unless a failing regression test demonstrates a core defect.

## Important Data Assumptions
- Roster analyzer uploads require core columns `player_name`, `multiplier`, `expires`, and `rarity`; `franchise`, `tradeable`, `team`, and `position` affect optional calculations.
- Its historical valuation expects `gameblazers.db` to contain `sales_history` with the columns queried in `app.py`; the database has no documented ingestion script in this repository.
- The optimizer accepts a roster/card CSV plus a raw weekly projection CSV and applies `raw_projection * multiplier` exactly once.
- Eligibility requires an Active card, a positive projection, and normalized name/position/team agreement.
- Keep generated uploads and database artifacts out of unrelated analysis changes, and verify the working directory when using relative paths.
- The roster analyzer uses a hardcoded Flask secret key and debug mode; replace configuration before any production deployment.
