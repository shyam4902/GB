# GameBlazers Football Optimizer V1 Readiness

**Audit date:** 2026-08-13  
**Scope:** Historical optimizer implementations, roster exports, weekly projection sheets, contest artifacts, saved lineup state, and existing discovery documents.  
**Purpose:** Record the evidence-backed V1 contract and the implementation boundary. The pure optimizer core is implemented; the Flask/UI boundary remains intentionally untouched.

## Evidence labels

- **User decision** — settled in the task brief and authoritative for V1.
- **Confirmed repository fact** — directly observed in source, data, or archived artifacts.
- **Historical evidence** — directly observed but dated or tied to an old prototype/rules snapshot.
- **Recommendation** — the narrowest safe implementation choice derived from the evidence.
- **Unresolved** — still requires a product/rules decision or current source verification.

---

## 1. Settled V1 product contract

These are **user decisions** for the first implementation:

1. V1 is a private, beginner-friendly football lineup optimizer for the owner and a few friends.
2. Roster valuation and completed-marketplace-sales research remain separate later work. Do not integrate either into the optimizer.
3. V1 consumes raw/unmultiplied player projections.
4. Adjusted projection is calculated exactly once:

   ```text
   adjusted projection = raw player projection × card multiplier
   ```

5. A card is eligible only when:
   - roster status is `Active`;
   - a projection player is successfully matched; and
   - raw projection is greater than zero.
6. Missing or zero projections are ineligible and naturally handle bye weeks.
7. Multiple cards for one athlete remain distinct candidate choices because salary and multiplier can differ.
8. A lineup cannot contain the same real athlete twice.
9. V1 returns one complete optimal lineup or a clear infeasible result—never a partial lineup.
10. No V1 roster-management page is required.
11. No fuzzy name matching may silently join players. Matching must normalize safe differences, require normalized name, position, and team equality, use only the demonstrated team aliases `LVR → LV` and `JAC → JAX`, and report unmatched rows visibly.
12. Inferno has eight players.
13. Flamethrower is confirmed for V1 as `QB, RB, WR, TE, Flex, Superflex`, six total players, `$60,000` cap.
14. Flex Appeal is included in V1 as `QB + five Flex` with a `$52,000` cap.
15. The historical 50% minimum salary rule is enabled in the settled V1 contest definitions below. It remains historical product evidence and should be revalidated before a public/current-rules release.

### V1 contest configuration

| Contest | Required slots | Cap | Status |
|---|---|---:|---|
| Spark | QB, RB, WR, TE | `$16,000`–`$32,000` | User-confirmed V1 configuration |
| Scorcher | QB, RB, WR, TE, Flex | `$18,375`–`$36,750` | User-confirmed V1 configuration |
| Wildfire | QB, RB, WR, TE, Flex, Flex | `$24,000`–`$48,000` | User-confirmed V1 display name; `Volcano` is a historical alias |
| Flex Appeal | QB, Flex, Flex, Flex, Flex, Flex | `$26,000`–`$52,000` | User-confirmed V1 inclusion |
| Flamethrower | QB, RB, WR, TE, Flex, Superflex | `$30,000`–`$60,000` | User-confirmed |
| Inferno | QB, RB, RB, WR, WR, TE, Flex, Superflex | `$32,000`–`$64,000` | User-confirmed; eight players |

`Flex = RB/WR/TE`. `Superflex = QB/RB/WR/TE`. The minimum values are the historical 50% rule now enabled in the settled private V1 configuration; they should be revalidated before a public/current-rules release.

---

## 2. Optimizer lineage

### 2.1 Meaningful versions and references

| Evidence family | What it actually does | V1 treatment |
|---|---|---|
| `dfs_optimizer.html:163-229` | Static golf page; parses two CSVs, maps names, builds card rows, and computes `base projection × multiplier` | Reuse the two-input concept and row representation, not the golf schema |
| `dfs_optimizer.html:311-367` | Exact recursive choose/skip search grouped by player name, with salary-cap pruning and a six-player objective | Correct exact-search reference; adapt slot feasibility and athlete groups for football |
| `lineup_optimizer/app.py:10-15` | Flask deployment target with Spark/Scorcher/Wildfire/Inferno configs; no Flamethrower | Retain route/deployment boundary only; replace solver behavior |
| `lineup_optimizer/app.py:96-141` | Fixed-order `nlargest()` greedy loop, repeated disjoint lineups, row-index removal, partial-lineup behavior | Reject as a solver; reuse only route/input context |
| `lineup_optimizer/newapp.py:94-141` | Slightly stricter greedy variant; removes names after selection and silently stops on failure | Reject as a solver; it still lacks global search and clear reasons |
| `GB2/app (2).py` | SHA-256 exact duplicate of `lineup_optimizer/app.py` | Historical duplicate, not an independent implementation |
| `GameBlazers/lineup optimizer/lineup_optimizer_standalone (1)`–`(9)` | Browser optimizer using alternate `Player/Positions/Salary/Status` schema, salary-derived projection, greedy slot filling, and multiple lineups | Historical behavior reference only; projection contract is incompatible with V1 raw projections |
| `GameBlazers/lineup optimizer/lineup_optimizer_standalone (10)`–`(12)` | Adds status validation, position normalization, explicit Flex/Superflex mapping, slot labels, and user-visible errors, but remains greedy | Best standalone parser/slot/error reference; do not reuse its optimization algorithm |
| `GameBlazers/lineup optimizer/lineup_builder.html`, `dfs_lineup_builder_fixed.html`, `GB_lineupBuilder_manual*.html` | Manual drag/drop slot builders with position validation and totals; no exact automatic solver | Historical UI behavior and slot semantics only |
| `GameBlazers/lineup optimizer/GBLv2.html`, `GBv2.1.html`, `GBv2.3.html`, `GBv2.4.html`, `GBv2.5.html` | Rich manual lineup-management UI: contest columns, locks/exclusions, game windows, projections, floor/ceiling, save state, and slot rendering | Best product-behavior/display reference; not an exact optimizer |
| `GameBlazers/lineup optimizer/testing.html`, `testa.html`, `trying.html` | Richer manual UI variants with five contests, score editing, exposure/player-finder concepts, and save behavior | Secondary UI reference; preserve ideas only after V1 correctness |
| `GameBlazers/lineup optimizer/*.json` | Saved mutable UI state keyed by contest and numeric slot positions | Fixture/state-shape reference only; not proof of valid lineups |

### 2.2 Canonical references for the next implementation

- **Golf exact-solver reference:** `dfs_optimizer.html`, especially `backtrack`/the recursive solver at lines `311-367`. It is exact for its own six-player, no-position problem, not directly reusable for football.
- **Football product-behavior reference:** `GameBlazers/lineup optimizer/GBv2.5.html`, whose slot rendering and contest-column behavior represent the richest manual UI family. Its `createPositionSlotHTML`/`createSlottedPlayerHTML` behavior is display logic, not optimization.
- **Football parser/slot/error reference:** `GameBlazers/lineup optimizer/lineup_optimizer_standalone (12).html`, lines `520-749`. It filters by status, validates required positions, maps Flex/Superflex in `getValidPositionsForSlot`, labels slot assignments, and reports errors, but `generateSingleLineup` is greedy and `selectBestPlayer` is value-based rather than globally optimal.
- **Deployment boundary:** `lineup_optimizer/app.py`, selected by `lineup_optimizer/Procfile:1`. Keep the boundary unless a later product decision explicitly changes it.

### 2.3 Why the newest-looking file is not canonical

The numbered standalone `(12)` file is newer in the filename sequence and has better validation/display behavior, but it still chooses one best affordable player at each slot (`lineup_optimizer_standalone (12).html:584-634`) and removes selected names to generate later lineups (`:543-556`). `GBv2.5.html` is larger and richer but is primarily a manual lineup manager. Neither is a correctness-preserving exact solver. Filename order therefore cannot select a canonical implementation by itself.

### 2.4 Smallest viable combination

The minimum combination is:

1. Keep the Flask upload/contest/result boundary from `lineup_optimizer/app.py` and `Procfile:1`.
2. Use the explicit slot vocabulary and input-validation ideas from standalone `(12)`.
3. Use conservative matching and raw projection × multiplier semantics from the settled contract and `Projections/GameBlazers.Rmd:111-135`.
4. Adapt the exact-search idea from `dfs_optimizer.html:311-367`, or use the already-declared PuLP dependency (`lineup_optimizer/requirements.txt:9`) for a binary assignment model.
5. Render one explainable result using the slot labels demonstrated by standalone `(12)`.

No wholesale rewrite, database migration, roster analyzer integration, marketplace integration, or new framework is required.

---

## 3. Roster and projection schema audit

### 3.1 Schema matrix

| File family | Headers/shape | Types and values | Projection status | Identity status |
|---|---|---|---|---|
| `GameBlazers/rosters/*.csv` raw exports, including `My_roster.csv`, `GB_roster.csv`, user rosters | `player_name, team, position, multiplier, salary, franchise, tradeable, expires, card_status, rarity, listed, league, status` | Position values `QB/RB/WR/TE`; multipliers observed `1`–`1.5`; salary integer-like; statuses include `Active`, `Injured Reserve`, `Inactive`, `Practice Squad`, `Suspended`, `Physically Unable to Perform` | No projection column; raw card-side input | No stable athlete ID or Item/card ID |
| `GameBlazers/rosters/Unknown copy.txt` | Same 13-column raw schema stored with `.txt` extension | CSV content despite extension | No projection | No stable ID; detect by headers/content, not extension |
| Derived game-window roster files | `player_name, team, position, multiplier, salary, status, Game Window, Bye Week` | Adds schedule-derived fields; schema casing differs from joined outputs | No numeric projection in the 8-column versions | No stable ID |
| Derived projection roster files | Same derived fields plus `Projection, Projection x Multiplier` | `Projection x Multiplier` is already adjusted | Adjusted projection is present; do not multiply again | No stable ID |
| `GameBlazers/rosters/active_roster_*` and `data/processed/updated_roster.csv` | `Player, position, multiplier, salary, status, game_window, SOS, Floor, Consensus, Proj., Ceiling, 3D Proj., GB_Projection, GB_Projection_Floor, GB_Projection_Ceiling` | Positions uppercase; `NA`/missing values occur; `GB_Projection` numeric where matched | `3D Proj.` is the base source field used by the R pipeline; `GB_Projection` and floor/ceiling fields are multiplier-adjusted | Player name only; no team in these joined files and no stable ID |
| `GameBlazers/projections sheets/Projections Sheet - {QB,RB,WR,TE} Wk{14,15,17}.csv` | Position-specific `Rank, Player, Matchup, ...` with weekly headers | Player strings include `Name POSITION TEAM`; Week 14 has extra DFS salary/value columns; Weeks 15/17 use shorter headers | `3D Proj.` is the raw/base projection for the historical R join; `Projection`/`Proj.` are alternate source projections | No athlete ID; team/position encoded in `Player` text |
| `GameBlazers/projections sheets/Projections Sheet.xlsx` | Four Week 14 sheets (`QB Wk14`, `RB Wk14`, `WR Wk14`, `TE Wk14`) with formatting/empty capacity | Workbook source artifact, not a normalized table | Contains source projection sheets; normalize before reuse | No stable ID |
| `GameBlazers/lineup optimizer/ExportedRoster_20250914082406.csv` and other alternate exports | `Player, Positions, Team, Multiplier, Overall, Franchise, Rookie, Tradeable, Salary, Collection, Status, Expires` | Positions are title-cased/possibly comma-delimited; status is `Active`/other; salary and multiplier string-like | No independent raw projection; `Overall` is not proven equivalent to weekly raw projection | No stable Item ID |
| Numbered standalone browser prototypes | Require variants of `Player`, `Positions`, `Team`, `Multiplier`, `Salary`, `Status`; often estimate projection from salary | Position normalization varies; malformed values often fall back to defaults | Salary-derived estimate, not authoritative GameBlazers projection | Synthetic IDs or names; no stable Item ID |

### 3.2 Projection contract conclusion

**Confirmed:** The R pipeline reads position-specific weekly sheets, joins by player name, and computes `GB_Projection = multiplier * 3D Proj.` (`Projections/GameBlazers.Rmd:111-135`). Existing joined CSVs therefore contain an already-adjusted field. The historical weekly sheets should be treated as raw/base inputs for the V1 contract when using `3D Proj.`; their encoded team suffix is mandatory for strict matching.

**Recommendation:** V1 should accept one narrow, explicit two-file contract:

- card file: `player_name`, `team`, `position`, `multiplier`, `salary`, `status`;
- projection file: `player_name`, `team`, `position`, `raw_projection`;
- projection mode explicitly labeled raw; and
- `adjusted_projection = raw_projection * multiplier` exactly once.

Support a small documented alias set (`Player`/`player_name`, `Position`/`position`, `Multiplier`/`multiplier`, `Salary`/`salary`, `Status`/`status`) at the boundary. Do not build a generalized import framework or silently accept `GB_Projection` as raw. Pre-joined `GB_Projection` support can be a separate explicit mode later.

### 3.3 Historical status and position observations

- Raw source exports include non-Active statuses; the old Flask app does not filter them (`lineup_optimizer/app.py:96-121`).
- Standalone `(12)` filters to `Status == 'Active'` and normalizes position names in `processPlayer` (`lineup_optimizer_standalone (12).html:300-390` approximately; exact function block spans the parser section before line 520).
- Positions in the weekly projections are encoded as `QB/RB/WR/TE` suffixes; source roster positions are already uppercase in the 13-column exports.
- Team abbreviations drift: historical projections use `LVR`/`JAC` in places where rosters use `LV`/`JAX`; `UNS` is not a safe known team.

---

## 4. Measured name-matching audit

### 4.1 Method

The audit compared every source-style roster row in 29 `GameBlazers/rosters/` exports against the corresponding position sheet for Weeks 14, 15, and 17. It covered **7,050 roster-row/week observations**. Repeated observations across snapshots are intentionally retained in the total because they show real ingestion workload, but they are not unique-player counts.

Progressive stages were:

1. exact display-name match against the raw projection string;
2. trim/case-fold against the raw projection string;
3. remove the projection suffix `POSITION TEAM` (`QB/RB/WR/TE` plus 2–3 letter team), then match;
4. normalize punctuation/apostrophes/hyphens; and
5. normalize demonstrated suffixes `Jr., Sr., II, III, IV`.

### 4.2 Results

| First successful stage | Rows | Share of 7,050 |
|---|---:|---:|
| Exact raw name | 0 | 0.00% |
| Case-fold/trim raw name | 0 additional | 0.00% |
| Strip projection position/team suffix | 5,771 | 81.86% |
| Punctuation normalization | 9 | 0.13% |
| Suffix normalization | 22 | 0.31% |
| Still unmatched | 1,248 | 17.70% |
| Ambiguous matches under position-specific matching | 0 | 0.00% |

The high unmatched count is not evidence that all names need aliases. The sheets and rosters are historical snapshots from different weeks, contain bye/inactive/stale roster entries, and do not cover every owned athlete. Examples from the canonical `GameBlazers/rosters/My_roster.csv` include players absent from a given week sheet such as Jayden Daniels, Derrick Henry, Terry McLaurin, and Dak Prescott.

### 4.3 Examples fixed by normalization

- Projection `Bucky Irving RB TB` → roster `Bucky Irving` after suffix removal.
- Projection `D.K. Metcalf WR SEA` → roster `DK Metcalf` after punctuation normalization.
- Projection `Deebo Samuel WR SF` → roster `Deebo Samuel Sr.` after suffix normalization.
- Projection `John Metchie WR HOU` → roster `John Metchie III` after suffix normalization.

No explicit player-name alias is required by the demonstrated historical mismatches after these safe transformations. The only explicit team aliases demonstrated by the data are `LVR → LV` and `JAC → JAX`; V1 applies them before required team comparison. Do not map `UNS` to a team.

### 4.4 Team/position confirmation and dangerous fuzzy matches

The raw scan found 176 team-conflict occurrences before accounting for historical abbreviation drift. In the canonical `My_roster.csv` audit, normalizing `LVR/LV` and `JAC/JAX` removed the observed team conflicts for matched Week 14/15/17 rows. For V1, team is a required match key: a name/position match with any other normalized team produces `team_mismatch` and remains ineligible. No fuzzy team aliases are permitted.

Examples where fuzzy matching would be dangerous include:

- `Brian Robinson Jr.` versus `Bijan Robinson`;
- `Zay Flowers` versus `Zay Jones`;
- `Noah Brown` versus `A.J. Brown` or `Dyami Brown`;
- `Malik Willis` versus unrelated nearby quarterback names; and
- similarly abbreviated initials such as `DK Metcalf` versus `D.K. Metcalf` (safe punctuation normalization) versus a genuinely different name.

**V1 decision:** normalize trim/case, Unicode apostrophes, punctuation, hyphens, and demonstrated suffixes; strip only the known projection position/team suffix; require normalized position and team equality after `LVR → LV` and `JAC → JAX`; report `team_mismatch` visibly; never fuzzy-match silently.

---

## 5. Duplicate-card behavior

### 5.1 Measured counts

The audit counted repeated player names, exact repeated visible rows, repeated `(name, team, position, multiplier, salary)` keys, and names with more than one multiplier/salary variant in each source-style export.

| File | Rows | Repeated names | Exact duplicate rows | Repeated visible attribute rows | Names with variants |
|---|---:|---:|---:|---:|---:|
| `GameBlazers/rosters/My_roster.csv` | 129 | 28 | 0 | 10 | 21 |
| `GameBlazers/rosters/My_roster_2.csv` | 126 | 24 | 0 | 11 | 17 |
| `GameBlazers/rosters/GB_roster (2).csv` | 170 | 42 | 0 | 20 | 31 |
| `GameBlazers/rosters/Corrected_Roster_with_Bye_Week_Adjustments.csv` | 98 | 12 | 6 | 6 | 7 |
| `GameBlazers/rosters/Jaz_roster.csv` | 41 | 5 | 0 | 1 | 4 |
| `GameBlazers/rosters/playoff_roster.csv` | 165 | 36 | 0 | 17 | 27 |

Representative variants include:

- `Jameson Williams`: multipliers `1.1`, `1.2`, and `1.5` in `My_roster.csv`;
- `Chuba Hubbard`: repeated rows with different multipliers/salaries and one repeated attribute combination;
- `Russell Wilson`: three identical visible attributes in `My_roster.csv`;
- `Hunter Henry`, `Mike Evans`, and `Antonio Gibson`: repeated visible attributes that cannot be proven distinct without an Item ID.

The larger already-joined optimizer sample similarly contains repeated names and repeated visible attributes, while the joined schema has no team or stable card ID.

### 5.2 What the historical optimizers did

- `lineup_optimizer/app.py:111-121` removes selected DataFrame rows by row index, so multiple cards for one athlete can be selected together.
- `lineup_optimizer/newapp.py:118-125` removes all later rows with a selected `Player` name, but it computes a multi-count selection before the removal; duplicate names can still appear twice in one `RB:2` or `WR:2` batch.
- `dfs_optimizer.html:315-328` groups by original name and selects at most one card per raw name, but it does not normalize football identities or use stable IDs.
- standalone `(12)` checks selected names within a generated lineup (`lineup_optimizer_standalone (12).html:598-610`), but it remains greedy and uses names as identity.

### 5.3 Narrowest safe V1 policy

1. Generate a synthetic source-row/card-row ID for diagnostics, never as proof of Item identity.
2. Normalize a conservative athlete key from the player name.
3. Preserve multiple rows for the same athlete when multiplier/salary differs; the solver may choose one variant.
4. Collapse exact visible duplicates for optimization when no Item ID exists, while retaining source row numbers/counts in diagnostics.
5. Enforce `sum(selected cards for athlete) <= 1` in the solver itself.
6. Never use salary or multiplier as identity. They are card attributes, not athlete identity.
7. Do not invent ownership-instance identity that the exports do not provide.

---

## 6. Contest-rule evidence matrix

| Rule/configuration | User decision | Archived official screenshot/reference | Later browser prototype | Old Flask | V1 treatment |
|---|---|---|---|---|---|
| Spark: QB/RB/WR/TE, `$32k` | Confirmed | `GameBlazers/contest details/Spark details.jpg`; dated Nov. 2024 contest snapshot | Present in standalone configs, e.g. `(9).html:201` | `app.py:10` | Include |
| Scorcher: +Flex, `$36.75k` | Confirmed | `Scorcher details.jpg` | Present, e.g. `(9).html:202` | `app.py:11` | Include |
| Wildfire: two Flex, `$48k` | Confirmed V1 display name; `Volcano` retained as historical alias | `Wildfire details.jpg` directly says Wildfire | Prototypes call the same shape Volcano, e.g. `(9).html:203`; rich UI uses Volcano | Flask calls it Wildfire, `app.py:12` | Use Wildfire; accept Volcano internally |
| Flamethrower: Flex + Superflex, six players, `$60k` | Confirmed by user; historical prototype corroborates | Not required to resolve V1 because user supplied the rule | `(9).html:204`; `testing.html:300` | Absent from `app.py:10-15` | Include in V1 config |
| Flex Appeal: QB + five Flex, `$52k` | Confirmed by user for V1 | Not established by the contest screenshots reviewed | `(9).html:205`; `(10).html:203`; `testing.html:301` | Absent | Include in V1 config |
| Inferno: eight slots, `$64k` | Confirmed | `Inferno Details.jpg` | `(9).html:206`; `testing.html:302` | `app.py:13-15` | Include with explicit eight slots |
| 50% minimum salary use | Historical evidence; enabled for settled private V1 configs | Spark/Scorcher/Wildfire/Inferno detail screenshots show 50% minimum (`GameBlazers/docs` inspection notes) | Browser UIs show salary bars but do not consistently encode minimum | Not enforced | Encode explicit contest minimums; revalidate before public release |
| Scoring | User did not settle current rules in this audit | `GameBlazers/Scoring info.jpg`, historical scoring image | Prototypes use projections/actual scores, not a canonical scoring engine | Not modeled | Preserve as dated fixture/reference, revalidate before scoring implementation |

### 6.1 Historical minimum-spend evidence

The archived contest-detail screenshots record:

- Spark: `$16,000` minimum on `$32,000` cap;
- Scorcher: `$18,375` minimum on `$36,750` cap;
- Wildfire: `$24,000` minimum on `$48,000` cap; and
- Flex Appeal: `$26,000` minimum on `$52,000` cap (settled V1 configuration based on the same 50% rule).
- Inferno: `$32,000` minimum on `$64,000` cap.

These remain dated rule evidence, but the private V1 implementation now encodes the settled minimum values explicitly per contest rather than universalizing a hidden default. Revalidate before a public/current-rules release.

### 6.2 Historical scoring snapshot

`GameBlazers/Scoring info.jpg` records: passing yards at 1 point per 25 yards, 300+ passing-yard bonus, passing TD +4, interception/fumble lost -1, rushing/receiving TD +6, rushing/receiving yards at 1 per 10, 100-yard bonus, reception +1, return TD +6, two-point conversion +2, and offensive fumble-recovery TD +6. It is a dated image, not a current machine-readable rules contract.

---

## 7. Exact solver requirements

Represent every contest as an ordered list of explicit slots, not only a position-count dictionary:

```text
Spark:        QB, RB, WR, TE
Scorcher:     QB, RB, WR, TE, FLEX
Wildfire:     QB, RB, WR, TE, FLEX, FLEX
Flex Appeal:  QB, FLEX, FLEX, FLEX, FLEX, FLEX
Flamethrower: QB, RB, WR, TE, FLEX, SUPERFLEX
Inferno:      QB, RB, RB, WR, WR, TE, FLEX, SUPERFLEX
```

For each eligible card `c` and slot `s`, allow assignment only when the card position is compatible. A binary assignment model can use:

1. every slot receives exactly one card;
2. each card row is used at most once;
3. each normalized athlete is used at most once;
4. salary is `<= maximum_salary`;
5. salary is `>= minimum_salary` using the explicit V1 contest definition; and
6. objective maximizes adjusted projection.

PuLP is declared in `lineup_optimizer/requirements.txt:9`, but it is not installed in the current environment. The implemented core therefore uses a dependency-free exact branch-and-bound search with salary-aware upper bounds, repeated-slot symmetry breaking, deterministic tie-breaking, and explicit infeasibility probes. Copying the golf recursion without positional assignment would be incorrect.

### Required result semantics

Return either:

- one complete assignment with contest, slot, player, position, normalized athlete key, source row/card ID, multiplier, salary, raw projection, adjusted projection, total salary, remaining cap, and total projection; or
- a structured infeasible result with a reason such as schema error, no eligible card for a required slot, duplicate-athlete conflict, minimum-spend failure, or no cap-feasible assignment.

Never return a partial lineup. A greedy failure is not proof of infeasibility.

---

## 8. Reusable versus rejected behavior

### Reuse or adapt

- Golf two-file upload and normalized card-row concept: `dfs_optimizer.html:163-229`.
- Golf raw projection × multiplier calculation: `dfs_optimizer.html:205-225`.
- Golf exact-search/pruning concept: `dfs_optimizer.html:311-367`.
- Standalone `(12)` status filtering, position normalization, Flex/Superflex mapping, slot labels, and visible error approach.
- `GBv2.5.html` manual UI ideas: explicit slot rendering, player pool, contest columns, game-window display, and later lock/exclude affordances.
- Existing Flask/Procfile deployment boundary.

### Reject unchanged

- Flask `nlargest()` loops and repeated disjoint-lineup behavior: `lineup_optimizer/app.py:96-141`.
- Alternate Flask greedy implementation: `lineup_optimizer/newapp.py:94-141`.
- Salary-derived projection estimate in standalone `(1)`–`(12)`; it violates the settled raw projection contract.
- Silent defaults such as malformed multiplier → `1`, salary → `0`, or missing projection → usable zero.
- Raw-name-only uniqueness without punctuation/suffix normalization.
- Browser prototype random IDs and saved JSON as a validity source.
- R Markdown external `~/Downloads` paths as a reproducible V1 dependency (`Projections/GameBlazers.Rmd:13-16`).
- Roster analyzer, marketplace, SQLite, external fantasy-values data, Tableau workbook, and scoring/market research in the optimizer implementation.

---

## 9. Fixture catalog

Created under `fixtures/optimizer_v1/`:

- `valid_cards.csv` / `valid_projections.csv`: one valid construction for Spark, Scorcher, two-Flex Wildfire, Flamethrower, and eight-player Inferno.
- `flex_appeal_cards.csv` / `flex_appeal_projections.csv`: minimal explicit QB-plus-five-Flex construction.
- `edge_cards.csv` / `edge_projections.csv`: punctuation/suffix matching, duplicate variants, exact visible duplicate, zero projection, missing projection, unmatched card, and non-Active status.
- `infeasible_missing_te_*`: missing-position infeasibility and no-partial-lineup case.
- `infeasible_salary_*`: salary-cap infeasibility and no-partial-lineup case.
- `greedy_counterexample_*`: expensive high-projection QB makes old fixed-order greedy exceed Spark cap; exact search can choose the slightly lower-projection affordable QB.
- `contest_cases.md`: expected slot shapes and eligibility assertions.
- `README.md`: contract and provenance, including the mandatory projection team field.

These fixtures are synthetic reductions grounded in the observed schemas and code. They intentionally omit stable Item IDs and do not introduce a test framework or production solver.

---

## 10. Safe cleanup result

The exact-duplicate audit found nine duplicate groups across the requested scope, including the three external `GameBlazers/` roster duplicates, the GB2 R/Flask duplicates, duplicate standalone/manual HTML versions, and the two Terms PDFs. SHA-256 values and canonical/reference choices are recorded in:

`docs/optimizer-v1-duplicate-manifest.md`

No file was deleted because every duplicate outside the canonical operational path remains inside a historically meaningful archive or legal-artifact path. No production source reference requires a duplicate pathname. `.DS_Store` files were not removed.

---

## 11. Remaining decisions and smallest implementation sequence

### Truly unresolved/product-dependent decisions

1. **Current-rule revalidation before public release:** the private V1 contract uses Wildfire, the historical 50% minimums, and Flex Appeal as settled by the owner; current GameBlazers rules should be rechecked before expanding beyond the private tool.
2. **Initial upload UX:** the recommended default is two files (raw projections + card roster), but a private tool could instead initially accept a pre-joined file under an explicitly labeled adjusted mode. The solver contract itself is settled as raw/unmultiplied for V1.

### Recommended implementation sequence

1. **Completed:** pure normalization boundary for the two explicit CSV inputs, preserving source row numbers and reporting schema/match/status exclusions.
2. **Completed:** six V1 contest definitions as explicit slot lists, including Flex Appeal, minimum salary, maximum salary, and the internal Volcano alias.
3. **Completed:** adjusted projection calculation and regression coverage proving the multiplier is applied exactly once.
4. **Completed:** exact slot-aware assignment with normalized-athlete uniqueness and no partial result.
5. **Completed:** focused tests using `fixtures/optimizer_v1/` for valid shapes, Flex/Superflex, duplicate cards, strict matching, ineligible rows, cap/position infeasibility, minimum-spend variants, and the greedy counterexample.
6. **Next:** expose one explainable lineup or a reasoned infeasibility result through the existing Flask boundary; do not add multiple lineups or marketplace/roster-analysis behavior.
7. Only after the boundary is verified, consider UI polish, downloads, card exclusions, multiple lineups, game windows, and saved sessions.

**Completed implementation task:** `lineup_optimizer/optimizer_core.py` now provides the pure input normalization + exact assignment core and is covered by `lineup_optimizer/test_optimizer_core.py` and `lineup_optimizer/test_optimizer_fixtures.py`.

---

## 12. Direct evidence index

- `dfs_optimizer.html:163-229` — golf parsing, merge, card representation, multiplier calculation.
- `dfs_optimizer.html:311-367` — exact golf recursive solver.
- `lineup_optimizer/Procfile:1` — Flask deployment target.
- `lineup_optimizer/app.py:10-15` — old contest dictionary.
- `lineup_optimizer/app.py:96-141` — greedy, row-index removal, repeated lineups, partial behavior.
- `lineup_optimizer/app.py:74-76` — unused PuLP imports.
- `lineup_optimizer/newapp.py:94-141` — alternate greedy behavior and silent stop.
- `lineup_optimizer/requirements.txt:9` — PuLP declaration.
- `Projections/GameBlazers.Rmd:13-24` — external weekly projection inputs and projection suffix stripping.
- `Projections/GameBlazers.Rmd:35-40` — roster fields.
- `Projections/GameBlazers.Rmd:111-135` — name joins and adjusted projection formula.
- `GameBlazers/lineup optimizer/lineup_optimizer_standalone (9).html:200-206` — historical six-contest config including Flex Appeal; V1 now confirms that contest.
- `GameBlazers/lineup optimizer/lineup_optimizer_standalone (12).html:520-749` — validation, greedy slot generation, slot mapping, errors, display.
- `GameBlazers/lineup optimizer/testing.html:255-302` — rich five-contest UI/config, including Flamethrower and Flex Appeal.
- `GameBlazers/lineup optimizer/GBv2.5.html` — richest manual UI family; function names include `processPlayer`, `createPositionSlotHTML`, `createSlottedPlayerHTML`, `updateLineupTotals`, `addEntry`, and `removeEntry`.
- `GameBlazers/contest details/*.jpg` — historical salary caps, slots, minimum-spend, entry limits, and dates.
- `GameBlazers/Scoring info.jpg` — dated scoring reference.
- `GameBlazers/payout tables/*` and `Fantasy_Football_Contest_Likelihoods_with_Payouts.csv` — historical payout evidence.
- `docs/gameblazers-folder-inspection-notes.md` — prior archive-wide image/PDF/HTML findings.
- `docs/gb2-inspection-notes.md` — prior GB2 classification.
- `docs/optimizer-v1-duplicate-manifest.md` — current exact-duplicate/cleanup record.
- `fixtures/optimizer_v1/` — minimal future implementation fixtures.
