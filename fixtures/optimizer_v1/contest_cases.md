# Fixture Case Catalog

## Valid contest shapes using `valid_cards.csv` + `valid_projections.csv`

All of these have at least one complete lineup under the settled private V1 minimum and maximum salaries and use distinct normalized athletes. The solver must assign explicit slots and return all required players, never a partial result.

| V1 contest | Slots | Minimum | Maximum | One valid construction |
|---|---|---:|---:|---|
| Spark | QB, RB, WR, TE | 16,000 | 32,000 | Patrick Mahomes, Bijan Robinson, Ja'Marr Chase, Travis Kelce = 30,500 |
| Scorcher | QB, RB, WR, TE, Flex | 18,375 | 36,750 | Patrick Mahomes, Chuba Hubbard, Ja'Marr Chase, Travis Kelce, Jonathan Taylor = 36,000 |
| Wildfire | QB, RB, WR, TE, Flex, Flex | 24,000 | 48,000 | Spark construction plus Chuba Hubbard and Jonathan Taylor = 42,500 |
| Flamethrower | QB, RB, WR, TE, Flex, Superflex | 30,000 | 60,000 | Spark construction plus Chuba Hubbard and Josh Allen = 44,500 |
| Inferno | QB, RB, RB, WR, WR, TE, Flex, Superflex | 32,000 | 64,000 | Patrick Mahomes, Bijan Robinson, Derrick Henry, Ja'Marr Chase, Justin Jefferson, Travis Kelce, Chuba Hubbard, C.J. Stroud = 59,500 |

`Flex` accepts RB/WR/TE. `Superflex` accepts QB/RB/WR/TE. `Volcano` is accepted by the core only as an internal historical alias for the V1 display name `Wildfire`.

## Flex Appeal fixture

`flex_appeal_cards.csv` + `flex_appeal_projections.csv` covers the settled six-player shape:

- QB, Flex, Flex, Flex, Flex, Flex;
- minimum salary 26,000;
- maximum salary 52,000; and
- exactly one QB plus five distinct RB/WR/TE athletes.

## Eligibility assertions from `edge_*`

Expected eligible cards after matching and filtering:

- `D.K. Metcalf` matches projection `DK Metcalf` after punctuation normalization.
- `Deebo Samuel Sr.` matches projection `Deebo Samuel` after suffix normalization.
- Both `Variant Athlete` rows remain distinct candidate cards, but at most one may be selected in a lineup.
- The two `Exact Duplicate Athlete` rows are indistinguishable without an Item ID; collapsing exact visible duplicates is safe for optimization, while preserving source row numbers for diagnostics is required.
- `Zero Projection Athlete` is ineligible because raw projection is zero.
- `Missing Projection Athlete` is ineligible because no projection row matches.
- `Unmatched Athlete` is ineligible and must be reported visibly, not fuzzy-joined.
- `Inactive Athlete` is ineligible because status is not `Active`.
- Projection teams are mandatory for matching; only `LVR → LV` and `JAC → JAX` are approved team aliases.
- No multiplier may be applied to a pre-adjusted field in these fixtures; adjusted values are raw projection × multiplier exactly once.

## Infeasibility assertions

- `infeasible_missing_te_*`: return an explicit missing-position/infeasible result for Spark; do not return the available QB/RB/WR as a partial lineup.
- `infeasible_salary_*`: return an explicit maximum-cap infeasible result; do not return an over-cap or partial lineup.

## Greedy counterexample

`greedy_counterexample_*` uses Spark with an expensive high-projection QB and a cheaper slightly lower-projection QB. The old fixed-slot greedy behavior picks the expensive QB and exceeds the cap; an exact solver should choose the cheaper QB and return a complete valid lineup.
