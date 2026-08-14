# Optimizer V1 Correctness Fixtures

**Created:** 2026-08-13  
**Purpose:** Small, human-readable implementation fixtures. These are not production data and do not implement a solver or test framework.

## Contract represented

- Cards use the raw roster-side contract: `player_name`, `team`, `position`, `multiplier`, `salary`, and `status`.
- Projections use raw/unmultiplied `player_name`, `team`, `position`, and `raw_projection`.
- A future implementation must calculate `adjusted_projection = raw_projection * multiplier` exactly once.
- Only `status == Active`, matched, positive-projection cards are eligible.
- A lineup may select only one card for a normalized real athlete, while distinct card variants remain available choices.
- Contest minimum and maximum salaries and slots are documented in `contest_cases.md`; the settled private V1 fixtures encode the historical 50% minimum explicitly per contest.

## Files

| File | Purpose |
|---|---|
| `valid_cards.csv` | Small active card pool with multiple card variants for some athletes and an exact repeated visible row |
| `valid_projections.csv` | Raw projections for the valid pool, including mandatory team values and punctuation normalization examples |
| `edge_cards.csv` | Status, zero/missing/unmatched, duplicate-variant, and exact-duplicate cases |
| `edge_projections.csv` | Team-aware projections for only the eligible/matching edge-case names |
| `infeasible_missing_te_cards.csv` / `infeasible_missing_te_projections.csv` | A no-TE case that must return a clear infeasible result and no partial lineup |
| `infeasible_salary_cards.csv` / `infeasible_salary_projections.csv` | A Spark-shaped pool whose only complete lineup exceeds the cap |
| `greedy_counterexample_cards.csv` / `greedy_counterexample_projections.csv` | The old slot-order greedy approach chooses an expensive QB and fails the cap, while an exact solver can choose the lower-scoring affordable QB |
| `flex_appeal_cards.csv` / `flex_appeal_projections.csv` | Minimal QB-plus-five-Flex fixture for the settled Flex Appeal contest |
| `contest_cases.md` | Expected slot shapes, minimum/maximum salaries, eligibility assertions, and scenario catalog |

## Provenance

`valid_*` and `edge_*` rows are synthetic minimal records designed from observed repository schemas. Names and field shapes are grounded in:

- `GameBlazers/rosters/My_roster.csv` and other 13-column roster exports;
- `GameBlazers/projections sheets/Projections Sheet - {QB,RB,WR,TE} Wk{14,15,17}.csv`; and
- `Projections/GameBlazers.Rmd:111-135`, which documents name joins and multiplier-adjusted `GB_Projection`.

The infeasibility and greedy cases are deliberately synthetic reductions of behaviors observed in `lineup_optimizer/app.py:96-141` and `lineup_optimizer/newapp.py:94-141`. They are not copied from a user's roster and contain no credentials or live data.

## What these fixtures do not claim

- They do not establish current GameBlazers contest rules.
- They do not provide stable Item IDs; the card rows intentionally omit one.
- They do not establish current public GameBlazers rules; the private V1 tests explicitly enable the settled per-contest minimum salaries.
- They do not replace testing against the historical CSVs after the core solver is correct.
