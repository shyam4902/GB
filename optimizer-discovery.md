# Optimizer Discovery Report

**Scope:** Read-only discovery for rebuilding the GameBlazers football lineup optimizer. Card valuation and marketplace behavior were intentionally excluded from the analysis except where an existing optimizer input schema made the boundary relevant.

**Repository inspected:** `/Users/shyampatel/Desktop/GB`

**Evidence labels used below:**

- **Confirmed** — directly observed in source or checked-in data.
- **Likely interpretation** — supported by code/data, but not an explicit product requirement.
- **Unresolved** — requires a product decision or an input that is not present in this repository.

## 1. Executive summary

### Findings

1. **`dfs_optimizer.html` is a standalone browser page, not a Flask application.** It loads Tailwind and PapaParse from CDNs, accepts two local CSV files, merges them in memory, and solves a fixed six-player, no-position lineup in JavaScript. There is no server route, backend entry point, deployment file, persistence, or download handler. Evidence: `dfs_optimizer.html:5-10`, `:28-57`, `:163-229`.
2. **The golf optimizer's main solver is exact for the six-item problem it actually constructs**, not greedy: it groups rows by original player name, recursively explores choosing one card or skipping each player group, enforces salary `<= cap`, and evaluates every feasible six-player result subject to its pruning bound. Evidence: `dfs_optimizer.html:311-367`.
3. **The golf page is not directly reusable for football without a positional adaptation.** Its solver has no position or slot concept and hardcodes six players. Its name map, column names, projection-file assumptions, and theoretical-ceiling calculation are golf-specific. Evidence: `dfs_optimizer.html:16`, `:128-134`, `:188-229`, `:232-309`.
4. **The active football deployment entry point is `lineup_optimizer/app.py`; `newapp.py` is an alternate implementation.** The `Procfile` points to `app.py`, which binds to `0.0.0.0` and reads `PORT`; `newapp.py` runs Flask debug mode and is not referenced by the `Procfile`. Evidence: `lineup_optimizer/Procfile:1`, `lineup_optimizer/app.py:173-177`, `lineup_optimizer/newapp.py:178-179`.
5. **Neither football implementation optimizes globally.** Both repeatedly build a lineup by taking the highest `GB_Projection` candidate for each slot in fixed dictionary order. `app.py` may emit partial lineups; `newapp.py` rejects a partial attempt but stops rather than searching alternatives. Evidence: `lineup_optimizer/app.py:96-141`, `lineup_optimizer/newapp.py:94-148`.
6. **The old football code does not correctly enforce one real athlete per lineup.** `app.py` drops selected DataFrame rows by index, so duplicate card rows for the same athlete can be selected together. `newapp.py` removes all rows matching `Player`, but it computes a multi-count selection before removing them, so duplicate names can still appear twice in one selected batch for a two-RB or two-WR requirement. Evidence: `lineup_optimizer/app.py:111-121`, `lineup_optimizer/newapp.py:110-125`.
7. **The confirmed football rules are not fully represented in code.** Spark, Scorcher, Wildfire, and Inferno are present with the stated caps and slot counts. Flamethrower is absent. Inferno's configured counts sum to eight, not nine. Evidence: `lineup_optimizer/app.py:10-15` and the identical `newapp.py:10-15`.
8. **The actual football data already contains multiplier-adjusted projections.** The R Markdown pipeline computes `GB_Projection = multiplier * 3D Proj.` (`Projections/GameBlazers.Rmd:131-135`), and the checked-in CSVs satisfy that formula for every non-missing row examined. A new implementation must choose one projection contract and multiply exactly once.
9. **There is no stable athlete/card identifier in the optimizer CSVs.** The current R pipeline joins by `Player` name after splitting by position (`Projections/GameBlazers.Rmd:111-127`), and the source roster export uses `player_name` but no card ID. Team and position are available in the raw roster, but neither is a stable card identifier. A v1 uniqueness key therefore has to be a normalized name unless a future export supplies IDs.
10. **The smallest safe implementation is an exact slot-aware solver inside the existing Flask football app, with the existing upload/route surface retained.** PuLP is already declared in `lineup_optimizer/requirements.txt:9` and imported in `app.py:76`, although the current code never uses it. A binary assignment model is a small adaptation, not a rewrite or database migration.

### Recommended v1 contract

- Retain the existing `lineup_optimizer` Flask application and `Procfile`.
- Retain the golf-style two-upload concept if the UI is being rebuilt around `dfs_optimizer`: one projection file containing **base** projections and one roster/card file containing card salary and multiplier.
- Normalize the current aliases (`Player`/`player_name`, `Multiplier`/`multiplier`, `Salary`/`salary`) at the boundary.
- Apply `card_projection = base_projection * multiplier` exactly once, or explicitly accept `GB_Projection` as already adjusted; do not infer silently between the two modes.
- Solve explicit football slots with an exact assignment/ILP model, salary `<=` cap, and one selected card per normalized athlete.
- Never return a partial lineup. Return a clear infeasible result when a required slot or cap-feasible eight/fewer-player assignment cannot be found.

## 2. Current golf optimizer: end-to-end behavior

### Runtime, framework, entry point, and deployment

**Confirmed:** `dfs_optimizer.html` is a single static HTML document. It has no Flask imports, server code, package manifest, `Procfile`, or API call. It depends on browser JavaScript plus two CDN scripts: Tailwind (`cdn.tailwindcss.com`) and PapaParse 5.4.1 (`cdnjs.cloudflare.com/.../papaparse/5.4.1/...`) at `dfs_optimizer.html:5-10`. It can be opened/served as a static page; the repository contains no documented deployment structure for it.

The page creates no persistent state. All data lives in `projData`, `rosterData`, `mergedPool`, `excludedCards`, `cardMap`, and `absoluteMaxCache` in the browser (`:123-134`). Reloading loses uploads, exclusions, and results.

### User flow and controls

1. The user selects a **Projections CSV** and a **Roster CSV** (`:28-50`).
2. PapaParse reads each file with `header: true` and `skipEmptyLines: true` (`:163-184`).
3. Once both parsed arrays are non-empty, `prepareData()` merges them and enables the button (`:181-185`).
4. The user enters a numeric max salary. The default is `64000`, and changing it re-solves immediately if a merged pool exists (`:52-57`, `:150-154`).
5. The user clicks **Generate Optimal Lineup** (`:57`, `:158`).
6. A selected result shows six rows with player, multiplier, salary, base projection, total projection, and an **Exclude Card** button (`:81-105`, `:383-413`).
7. Excluding a card adds its synthetic row ID to a set and re-solves. The page can clear all exclusions or add an excluded row back (`:436-470`).

There is no contest selector, roster-size control, positional control, minimum/maximum salary control, status filter, projection mode selector, or download/export control. A repository-wide search found no download handler in this page.

### Upload columns, parsing, and normalization

**Projection CSV expected columns:**

- `First Name`
- `Lastname`
- `proj.`
- For the separate theoretical ceiling calculation only: `salary(1.0` (the literal property name in source is missing a closing delimiter and is fragile), at `:245-247`.

The code concatenates `First Name + " " + Lastname`, trims the result, and stores `parseFloat(p['proj.']) || 0` in an object keyed by full name (`:188-196`). If projection names repeat, the last row silently overwrites earlier rows.

**Roster CSV expected columns:**

- `Player`
- `Multiplier`
- `Salary`

For each roster row, the code uses `Player`, applies the three-entry golf-specific alias map, parses `Multiplier` as a float with fallback `1`, and parses `Salary` as an integer with fallback `0` (`:128-134`, `:205-223`). Rows whose mapped name is absent from the projection map are silently omitted. There is no schema check, type validation, row-level error display, or use of PapaParse's `results.errors`.

**Golf-specific name normalization:**

```text
Alexander Noren   -> Alex Noren
Christopher Gotterup -> Chris Gotterup
Matt McCarty      -> Matthew McCarty
```

This is a manual golf alias table at `:128-134`; it should not be carried into football.

**Important stale-state behavior:** if one file is replaced with an empty or invalid parse after a valid merge, the callback does not reset `mergedPool` or disable the button because `prepareData()` is only called when both arrays remain non-empty (`:181-185`). A user can therefore see/solve stale data after a failed replacement upload.

### Merge representation and multiplier calculation

Each matched roster row becomes a card object:

- `id: p_<roster index>`
- `originalName`
- `mappedName`
- `multiplier`
- `salary`
- `baseProj`
- `totalProj = baseProj * multiplier`

Evidence: `dfs_optimizer.html:205-225`.

This is the right basic calculation for raw base projections. It assumes the projection file's `proj.` is not already multiplier-adjusted. The current football files in this repository use a different, already-adjusted `GB_Projection` field; see Section 4.

### Main optimization algorithm: exact versus heuristic

**Confirmed:** the main golf solver is a custom recursive branch-and-bound search, not a greedy loop and not an external optimization package. It:

- removes excluded cards;
- groups remaining card rows by `originalName`;
- sorts card options within each group by total projection descending;
- sorts groups by their best option descending;
- recursively branches on every card option in a group and on skipping the group;
- rejects a branch when the salary cap would be exceeded;
- stops only after selecting six distinct name groups; and
- retains the highest projection feasible six-card lineup.

Evidence: `dfs_optimizer.html:311-367`.

For finite rows with numeric projections, the pruning bound is a valid optimistic upper bound for this constructed problem: the remaining groups are globally ordered by their best available projection, and the bound adds the best option from the next required number of groups while ignoring salary restrictions. Ignoring salary can only overestimate what a branch can achieve. Therefore the solver is **exact for the merged pool as represented**, with these qualifications:

- it solves exactly six items, regardless of any football contest;
- uniqueness is by the raw `originalName` string, not a stable athlete ID or normalized identity; and
- the result is only as good as the rows that survived the silent merge and parsing fallbacks.

The algorithm has no memoization. Large pools with many card variants can still have exponential worst-case behavior, and a browser tab can become unresponsive.

### Salary-cap behavior

The main solver enforces `currentSalary + player.salary <= currentMaxSalary` during recursion (`:330`, `:356-359`). It allows unused cap and maximizes points, not salary utilization. Invalid/missing salaries become zero in the merge (`:212-213`), which can make malformed cards artificially attractive.

The page also calculates a separate DP “absolute max” for six items (`:232-309`). That DP is not the same problem as the main solver:

- it uses every projection row rather than matched roster rows;
- it generates every combination of `1.0` plus every multiplier observed in the roster, even if a particular player does not have that card;
- it derives salary from a projection-file base-salary column rather than the actual roster card salary;
- it ignores exclusions; and
- it is still hardcoded to six.

Consequently, the displayed viability denominator is a theoretical number that can be unattainable by the uploaded roster. It is not a correctness check for the selected lineup (`:372-379`, `:414-430`).

### Player/card uniqueness and exclusions

The main solver enforces at most one row per `originalName` group (`:315-328`). Multiple cards for one name may exist and the solver may choose the best card that fits the cap. Each row receives a synthetic index-based ID, so exclusions are card-row exclusions, not athlete exclusions (`:205-225`, `:436-443`).

Fragile cases:

- Two spellings of one athlete create two groups.
- Two distinct athletes with the same raw name would be incorrectly merged.
- Exact duplicate CSV rows receive different synthetic IDs, but only one can be selected because of the name group; exclusion of one duplicate can leave the other available.
- No roster status, position, team, or expiration column is read.

### Result display and errors

Success displays six cards and totals for salary and points. It sorts the selected rows by salary descending before rendering (`:383-413`). It does not show slots or positions because the golf input has none. There is no download, permalink, saved lineup, or JSON output.

Failure displays a static message stating that a valid six-player lineup could not be found under the cap and resets totals (`:367-381`). The page can still calculate/show the theoretical DP ceiling, which may be unrelated to the actual available roster.

No explicit CSV parse errors, missing-column errors, unmatched-name report, invalid-number report, or slow-solver indicator is shown.

## 3. Current football optimizer: end-to-end behavior

### Runtime and deployment boundary

`lineup_optimizer/app.py` is the deployed/active entry point because `lineup_optimizer/Procfile:1` contains `web: python3 app.py`. It is a Flask app using pandas and Werkzeug (`app.py:1-6`), creates/uses a relative `uploads` directory (`:18-23`), and runs on `0.0.0.0` with `PORT` defaulting to 5000 (`:173-177`).

`lineup_optimizer/newapp.py` is a second Flask implementation with the same routes and almost the same code. It is not referenced by the `Procfile` and runs `app.run(debug=True)` (`newapp.py:178-179`). It should be treated as an alternate/older implementation, not a second production entry point.

The root roster analyzer is a separate Flask app. Its `/lineup_optimizer/` route is only a visual placeholder (`GB_roster_analyzer/app.py:240-248` and `GB_roster_analyzer/templates/lineup_optimizer_placeholder.html:1-158`); it does not invoke either football optimizer.

### Contest configuration compared with confirmed rules

Current `app.py` and `newapp.py` define the same four configurations (`:10-15`):

| Contest | Current slots | Current cap | Confirmed v1 rule | Finding |
|---|---|---:|---|---|
| Spark | QB 1, RB 1, WR 1, TE 1 | $32,000 | Same | Confirmed match; 4 players |
| Scorcher | Spark + Flex 1 | $36,750 | Same | Confirmed match; 5 players |
| Wildfire | Spark + Flex 2 | $48,000 | Same | Confirmed match; 6 players |
| Flamethrower | Missing | Missing | Spark + Flex 2 | **Missing; provisional rule is not represented** |
| Inferno | QB 1, RB 2, WR 2, TE 1, Flex 1, Superflex 1 | $64,000 | Same | Confirmed match; counts sum to 8 |

The position candidate logic is:

- fixed position slot → that exact `position` value;
- Flex → `RB`, `WR`, or `TE`;
- Superflex → `QB`, `RB`, `WR`, or `TE`.

Evidence: `app.py:104-109` and `newapp.py:104-109`. The code does not assign or display a slot label in the result, so a selected row does not say whether it occupied a fixed, Flex, or Superflex slot.

### Upload and processing flow

1. `GET /` returns a minimal HTML form with one file input (`app.py:28-38`; same in `newapp.py`).
2. `POST /upload` requires a field named `file`, a non-empty filename, and a `.csv` extension (`:40-52`). It sanitizes the uploaded filename and saves it to the relative `uploads` directory.
3. It redirects to `/process/<filename>` (`:47-52`).
4. `GET /process/<filename>` calls `pd.read_csv()` and writes the unchanged DataFrame to `uploads/processed_roster.csv` (`:54-72`). This is only a copy; it does not normalize or validate the schema.
5. `/lineups` reads that fixed `processed_roster.csv` path for every request (`:78-82`). A missing file or malformed schema becomes a server error rather than a user-facing validation result.
6. `GET /lineups` returns a contest dropdown with only Spark, Scorcher, Wildfire, and Inferno (`:159-170` in `app.py`; `:166-176` in `newapp.py`).
7. `POST /lineups` selects a contest, reads its requirements/cap, generates repeated lineups, and renders raw HTML tables with totals (`app.py:84-154`; `newapp.py:84-161`).

Unlike the golf page, the football app currently accepts only one CSV. The checked-in examples are already merged roster/projection files.

### Actual generation behavior in `app.py`

For every iteration, `app.py`:

- copies the full DataFrame to `available_players`;
- loops through the contest dictionary in insertion order: QB, RB, WR, TE, Flex, Superflex;
- filters by allowed positions;
- takes `candidates.nlargest(count, 'GB_Projection').head(count)`;
- adds salary and `GB_Projection`; and
- drops each selected row by its pandas row index.

Evidence: `app.py:96-121`.

This is a **greedy, slot-order-dependent heuristic**. It never compares alternatives across slots, never trades a fixed-position choice for a better Flex/Superflex allocation, and never searches the salary-feasible combination space.

After a pass, it appends the selected rows only if the total salary is under the cap (`:127-135`). It then tries to build another disjoint lineup from the remaining DataFrame (`:137-141`). Thus the endpoint produces a sequence of disjoint greedy lineups, not the single globally optimal lineup requested for the rebuild. A high-value early choice that makes the pass too expensive is discarded only after the entire greedy pass, with no alternative search.

### Actual generation behavior in `newapp.py`

`newapp.py` uses the same contest order and `nlargest()` selection (`:94-125`) but adds two explicit checks:

- if fewer than `count` candidates exist, it raises `ValueError` (`:110-116`);
- if the constructed pass exceeds the cap, it raises `ValueError` (`:127-129`).

The exception is caught and the outer loop stops silently (`:136-141`). This prevents an intentionally partial result, but it is still not optimization: it does not try a cheaper or lower-projection alternative, and it does not tell the user whether the roster was genuinely infeasible or merely defeated by the greedy choice.

### Duplicate-player behavior

**`app.py` confirmed bug:** row-level removal by DataFrame index (`:117-121`) treats each duplicate CSV row as a separate player. The sample football data has repeated real names and even repeated card-attribute rows, so two cards for the same athlete can enter the same lineup if both are among the top candidates for a required slot or for separate slots.

**`newapp.py` partial fix with a remaining bug:** after adding each selected row it filters out all rows where `Player` matches (`:121-125`). That enforces name uniqueness across later slot iterations, but `nlargest(count, ...)` is calculated before the loop removes names. If two duplicate-name rows are both in the selected batch for `RB: 2` or `WR: 2`, the second stale row is still appended and counted. It can therefore output the same real player twice.

Neither version has a stable athlete key, name normalization, or a separate card identifier.

### Partial lineups and missing data

In `app.py`, an empty candidate set executes `continue` (`:111-116`) rather than failing the lineup. A position with fewer than the requested count also returns fewer rows from `nlargest()` without raising. If the resulting partial set is under the cap, it is appended (`:127-135`). This is the confirmed partial-lineup bug.

`newapp.py` rejects candidate shortages, but only with a generic silent break. Both versions lack explicit required-column checks and do not filter `status`. The data contains `Active`, `Injured Reserve`, and `Practice Squad` rows; all are eligible to the code if they have usable numeric projections.

Missing projection values are present in the actual CSVs. `nlargest()` and arithmetic are left to pandas; no explicit policy is applied for `NA`/NaN rows. There is no user report of dropped/missing projection rows.

### Unused dependencies and code

- `lineup_optimizer/app.py:74` imports `itertools.combinations`, but it is never used.
- `app.py:76` imports `LpMaximize`, `LpProblem`, `LpVariable`, and `lpSum` from PuLP, but no PuLP model is created anywhere in the file. This is a declared dependency (`requirements.txt:9`) and a useful existing foundation for an exact v1 solver, not evidence that the current app is optimized.
- `newapp.py:74` imports `combinations` but does not import or use PuLP.
- Both implementations import `render_template` but return hand-built HTML strings for the optimizer.
- `lineup_optimizer/Test.py` is a scratch dice-printing script, not a test suite.

### Result behavior

Both implementations render each generated lineup using `DataFrame.to_html(index=False)` followed by total salary, salary remaining, and total projected points (`app.py:142-154`; `newapp.py:149-161`). There is no slot assignment in the output, no download, no JSON response, no infeasibility detail, and no exclusion control.

## 4. Input/data schema comparison

### Files actually present

A read-only inventory found five CSV files relevant to roster/projection behavior:

| File | Rows × columns | Role | Key columns and representative values |
|---|---:|---|---|
| `data/raw/My_roster.csv` | 129 × 13 | Raw game roster export | `player_name`, `team`, `position`, `multiplier`, `salary`, `franchise`, `tradeable`, `expires`, `card_status`, `rarity`, `listed`, `league`, `status`; e.g. `Jayden Daniels,WAS,QB,1.3,9750` at line 3 |
| `data/processed/updated_roster.csv` | 114 × 15 | Existing joined football projection output | `Player`, `position`, `multiplier`, `salary`, `status`, `game_window`, `SOS`, `Floor`, `Consensus`, `Proj.`, `Ceiling`, `3D Proj.`, `GB_Projection`, and multiplier-adjusted floor/ceiling; header at line 1 |
| `lineup_optimizer/uploads/active_roster_shyam_copy.csv` | 129 × 15 | Larger already-joined optimizer input | Same 15-column schema; header line 1; includes `Jayden Daniels` with `GB_Projection=24.96` at line 2 |
| `lineup_optimizer/uploads/active_roster_jaz_copy.csv` | 41 × 15 | Smaller already-joined optimizer input | Same 15-column schema; header line 1; includes seven QB, 13 RB, 15 WR, six TE rows |
| `lineup_optimizer/uploads/processed_roster.csv` | 41 × 15 | Copy consumed by the Flask app | Same schema as `active_roster_jaz_copy.csv`; header line 1 |

There is **no projection-only CSV in the repository** matching the golf page's `First Name`, `Lastname`, `proj.` contract. The football R Markdown references external files under `~/Downloads` (`Projections/GameBlazers.Rmd:13-16`, `:35`), so those source projection files could not be inspected here.

### Type and value observations

- Positions are exactly `QB`, `RB`, `WR`, `TE` in all inspected football CSVs. Counts are 24/39/46/20 in `active_roster_shyam_copy.csv`, 7/13/15/6 in the 41-row sample, and 22/39/35/18 in `data/processed/updated_roster.csv`.
- Multipliers are numeric values from `1.0` through `1.5`, with six observed values: `1`, `1.1`, `1.2`, `1.3`, `1.4`, `1.5`.
- Salaries are integer-valued card salaries. The 129-row joined sample ranges from `$3,740` to `$11,620`; the 41-row sample ranges from `$3,720` to `$12,900`; `data/processed/updated_roster.csv` ranges from `$3,520` to `$11,200`.
- `GB_Projection` is numeric where available and ranges from 4.08 to 27.45 in the 129-row joined sample. The value is already multiplier-adjusted.
- `status` contains `Active`, `Injured Reserve`, and `Practice Squad` in the larger sample. `card_status` in the raw export is `ACTIVE` for all 129 rows examined. The football optimizer does not use either status field.
- Raw `team` values are NFL abbreviations such as `GB`, `WAS`, `LV`, and `CIN`. `team` is not present in the already-joined optimizer CSVs.
- Some football CSV fields contain the literal text `NA`, which pandas reads as missing by default. Missing projection rows include `Dak Prescott`, `J.K. Dobbins`, `David Montgomery`, and `K.J. Osborn` in `data/processed/updated_roster.csv` (`:19`, `:30`, `:45`, `:86`), and 12 rows in `active_roster_shyam_copy.csv`, including `Skylar Thompson`, `Malik Willis`, `Bucky Irving`, `Breece Hall`, `DJ Moore`, and `Will Dissly` (`:7`, `:15`, `:50`, `:53`, `:58`, `:90`, `:124`).

### How projection rows are produced and joined

The R pipeline:

1. Reads four position-specific projection files from `~/Downloads` (`Projections/GameBlazers.Rmd:13-16`).
2. Removes a trailing two/three-letter team and position suffix from each projection `Player` field (`:21-24`).
3. Reads the roster and retains `player_name`, `position`, `multiplier`, `salary`, `status`, and `team` (`:35-40`).
4. Removes bye-team rows and renames the roster name column to `Player` (`:59`, `:96-104`).
5. Splits the roster by position and performs four `left_join(..., by = "Player")` operations (`:111-127`).
6. Computes `GB_Projection = multiplier * 3D Proj.` and corresponding floor/ceiling fields (`:131-135`).

Therefore, **the current join key is the player name**. Position-specific splitting reduces accidental cross-position matches, but the join itself is not based on a card ID or athlete ID. The current football Flask app receives the already-joined result and does no join at all.

### Names, punctuation, and stable identifiers

Names in the actual files include punctuation and suffixes such as:

- `C.J. Stroud`
- `D'Andre Swift`
- `J.K. Dobbins`
- `T.J. Hockenson`
- `Brian Robinson Jr.`
- `Michael Penix Jr.`

The football source has no explicit alias map. The golf page's alias map is unrelated and only covers three golfers (`dfs_optimizer.html:128-134`). A conservative normalization should trim and case-fold names and use a small explicit alias table only when a verified source mismatch exists; broad punctuation stripping or fuzzy matching could merge distinct people.

No optimizer CSV contains a stable card or athlete identifier. The raw export has `player_name` but no ID column. Team and position can validate a name match but are not sufficient card identity. A synthetic row ID can distinguish input rows for display/exclusion, but it cannot prove that two same-name rows are different real athletes.

### Duplicate cards and duplicate athlete rows

The actual files demonstrate why row-level selection is insufficient:

- `data/raw/My_roster.csv` has 28 duplicated player names among 129 rows and 9 repeated `(player_name, team, position, multiplier, salary)` keys. Examples include repeated `Russell Wilson` at lines 56, 93, and 115, and `Jameson Williams` with different multipliers at lines 9, 33, and 69.
- `active_roster_shyam_copy.csv` has 28 duplicated names and nine repeated `(Player, position, multiplier, salary)` keys, including `Russell Wilson` three times, `Chuba Hubbard` three times, and `Ladd McConkey` twice (`:17-19`, `:50-53`, `:88-89` show representative repeated/missing rows).
- `data/processed/updated_roster.csv` has 25 duplicated names and nine repeated attribute keys, including `Russell Wilson` at lines 3 and 5.
- `active_roster_jaz_copy.csv` has five duplicate names and one exact duplicate attribute key: `Quentin Johnston` twice.

Some repeats have different multiplier/salary and are clearly candidate card variants. Some exact repeats may be duplicate export rows. Because no card ID is present, v1 should either collapse exact duplicate attribute rows or preserve them only as equivalent synthetic rows while enforcing athlete uniqueness. Keeping exact duplicates cannot improve a one-card-per-athlete optimum, but it can make exclusion semantics ambiguous.

### Projection multiplier ambiguity

**Confirmed:** the R pipeline's source projection is `3D Proj.` and its output `GB_Projection` is already `multiplier * 3D Proj.` (`Projections/GameBlazers.Rmd:131-135`). The checked-in data was independently checked: all non-missing rows tested matched the formula to rounding tolerance.

**Unresolved:** the future upload contract may provide either raw projections or the existing joined CSV. Applying a multiplier to `GB_Projection` again would double-adjust the score. V1 should make the mode explicit rather than guessing from column names.

## 5. Confirmed bugs and limitations

### Golf page

1. **No schema validation or parse-error reporting:** malformed headers, PapaParse errors, and invalid rows are not shown (`dfs_optimizer.html:163-185`).
2. **Silent row loss on unmatched names:** only rows whose mapped roster name exists in the projection map enter `mergedPool` (`:205-225`).
3. **Silent numeric fallbacks:** malformed multiplier becomes `1`; malformed salary becomes `0`; malformed projection becomes `0` (`:195`, `:212-213`).
4. **Golf-only identity logic:** uniqueness is raw `originalName`, with no team/position/stable ID (`:315-319`).
5. **Hardcoded six-player objective:** UI and both solver paths assume six (`:16`, `:260`, `:335`).
6. **Theoretical max is not the uploaded-roster max:** the DP uses all projection players and synthetic multiplier variants, not matched cards or exclusions (`:232-309`).
7. **Stale state after failed/empty replacement upload:** old merged data may remain (`:181-185`).
8. **Potential UI freeze:** recursive search has no memoization and can grow combinatorially for a large card pool (`:334-367`).
9. **No result download or persistence:** there is only DOM rendering; no download/export code exists.
10. **External CDN dependency:** the page is not self-contained/offline because Tailwind and PapaParse are loaded from CDNs (`:7-10`).
11. **Raw HTML interpolation:** player names are inserted into result HTML without escaping (`:396-406`), a robustness/security concern if uploaded CSVs are untrusted.

### Football `app.py`

1. **Greedy rather than globally optimal:** `nlargest()` is run independently per slot (`:104-120`).
2. **No one-athlete constraint:** row indexes are dropped, not real-player groups (`:117-121`).
3. **Partial-lineup bug:** empty or undersized candidate sets are not rejected (`:111-116`).
4. **No exact fallback after cap failure:** a greedy pass is simply not appended if over cap (`:127-135`).
5. **Produces repeated disjoint lineups, not a best lineup:** `available_players` persists across iterations (`:96`, `:137-141`).
6. **No required-column/type/status validation:** `pd.read_csv()` is followed directly by optimization (`:59`, `:81-82`).
7. **Missing data policy is undefined:** NaN projections are left to pandas and can produce incomplete or non-useful results.
8. **Flamethrower is absent:** contest configuration only covers four names (`:10-15`).
9. **Unused PuLP imports:** the exact dependency exists but is not used (`:74-76`; `requirements.txt:9`).
10. **Unused `combinations` import:** `:74`.
11. **Poor infeasibility reporting:** no distinction between missing schema, missing position, cap infeasibility, and greedy failure.
12. **No slot labels, exclusion controls, download, or machine-readable result.**
13. **Fixed shared upload filename:** concurrent users can overwrite `uploads/processed_roster.csv` (`:62`, `:81`).

### Football `newapp.py`

1. **Still greedy:** same `nlargest()` approach (`:104-125`).
2. **Stale selected batch can duplicate an athlete:** name removal occurs after `nlargest(count)` has already selected rows (`:118-125`).
3. **Silently stops after shortages or cap failure:** caught `ValueError` produces no reason in the response (`:136-141`).
4. **No global alternative search, no schema validation, no status policy, no download, and no slot labels.**
5. **Not the declared deployment entry point:** `Procfile` selects `app.py`, not `newapp.py`.

### Data/pipeline limitations

1. No source projection-only files are checked in, so the future two-file contract cannot be validated against the original weekly projection schema here.
2. Existing checked-in football inputs are already adjusted outputs, while the golf page expects a raw projection plus a separate roster. Treating them identically would risk double multiplication.
3. Name-only joins and missing IDs make identity correctness depend on exact spelling/normalization.
4. The data contains exact duplicate rows and rows for non-active statuses; policy is not encoded in the optimizer.
5. The two nested Git repositories had pre-existing status changes when inspected (`lineup_optimizer`: deleted `uploads/My_roster.csv` and a type change for `gameblazers.db`; `GB_roster_analyzer`: no status output observed). No source/data file was changed for this report.

## 6. Reusable components

### Reuse directly or conceptually

- **Two-file browser upload pattern from golf:** separate projection and roster inputs, parse each, merge before solve (`dfs_optimizer.html:163-229`). For Flask, retain the concept but use request uploads and a validated server-side normalized table.
- **Projection × multiplier calculation:** golf's `baseProj * multiplier` (`dfs_optimizer.html:217-222`) matches the R pipeline when the input projection is raw.
- **Card-row representation:** a row-level synthetic ID, original display name, salary, multiplier, base projection, and adjusted projection is a useful normalized object (`dfs_optimizer.html:214-225`).
- **Exact-search mindset:** golf's choose/skip branch-and-bound (`dfs_optimizer.html:334-367`) demonstrates the required correctness property. Football needs slot feasibility added; it cannot be copied unchanged.
- **Salary constraint:** both golf's main solver and the desired football model use a strict `<=` cap (`dfs_optimizer.html:356`, `lineup_optimizer/app.py:127`).
- **Exclusion set concept:** `excludedCards` is a simple card-row filter (`dfs_optimizer.html:123`, `:315-318`, `:436-443`). It is optional for the simplest football v1.
- **Existing Flask boundary:** keep the current `lineup_optimizer/app.py` upload/contest/result routes and deployment structure rather than introducing a new framework.
- **Existing PuLP dependency declaration:** `requirements.txt:9` and `app.py:76` already provide the intended dependency location for an exact model, though installation should be verified in the app environment rather than assumed.

### Do not reuse unchanged

- Golf aliases and golf column names (`dfs_optimizer.html:128-134`, `:190-196`).
- Golf fixed-size six-player DP/viability calculation (`:232-309`).
- Golf identity grouping by raw name (`:315-319`) without a football identity policy.
- Football greedy `nlargest()` loops (`lineup_optimizer/app.py:104-120`, `newapp.py:104-125`).
- Football's repeated-disjoint-lineup behavior; v1 should define whether it returns one optimum or a deliberate multi-lineup feature. The stated rebuild requirement supports one optimum first.
- R Markdown's external path assumptions and manual schedule/bye logic unless projection generation itself is later made reproducible. The optimizer only needs the resulting projection rows for v1.
- Roster valuation, marketplace, SQLite, and unrelated templates. They are outside this optimizer rebuild boundary.

## 7. Minimum football adaptation

### Exact model

The smallest correct model is an assignment model over normalized card rows and explicit contest slots.

Create one slot object for each required position, for example:

```text
Spark:       QB, RB, WR, TE
Scorcher:    QB, RB, WR, TE, FLEX
Wildfire:    QB, RB, WR, TE, FLEX, FLEX
Flamethrower:QB, RB, WR, TE, FLEX, FLEX
Inferno:     QB, RB, RB, WR, WR, TE, FLEX, SUPERFLEX
```

For each card row `c` and slot `s`, define binary `x[c,s]` only when the card's position is allowed in that slot.

Constraints:

1. Every slot receives exactly one card: `sum_c x[c,s] = 1`.
2. A card row is used at most once: `sum_s x[c,s] <= 1`.
3. A real athlete is used at most once: `sum_(c belongs to athlete a, s) x[c,s] <= 1`.
4. Salary is within the contest cap: `sum_(c,s) salary[c] * x[c,s] <= cap`.
5. Maximize `sum_(c,s) projection[c] * x[c,s]`.

The compatibility sets are:

- fixed QB/RB/WR/TE slots → only that position;
- Flex → RB/WR/TE;
- Superflex → QB/RB/WR/TE.

Explicit slot variables prevent Flex or Superflex from being counted twice and naturally handle the fact that an RB/WR/TE can fill either a fixed slot or an eligible extra slot. They also make the output explainable: each selected card can be labeled with its assigned slot.

PuLP is a reasonable smallest implementation because it is already declared and imported. A custom Python branch-and-bound adaptation of golf is also possible, but it must carry slot feasibility and athlete-group constraints; copying the golf six-item recursion would be less direct than using the existing exact-model dependency.

### Enforce one card per real athlete

Normalize a conservative athlete key:

1. trim surrounding whitespace;
2. case-fold for comparison while preserving original display text;
3. apply only verified explicit aliases; and
4. keep team/position as validation metadata, not as a way to allow two same-name rows.

For v1, with no stable IDs in the CSVs, use that normalized name key for the athlete constraint. Give every input row a synthetic card-row ID for diagnostics and future exclusions. Do not use salary or multiplier as identity: the same athlete can legitimately have multiple card variants.

Exact duplicate rows should be collapsed for optimization if no stable card ID exists. Whether they are collapsed or retained, the athlete constraint must make them unable to create a second lineup slot.

### Projection and multiplier policy

Recommended v1 input contract:

- projection file: canonical player name, position, and one **base** projection column;
- roster/card file: canonical player name, position, multiplier, salary, and optional status/team metadata;
- adjusted projection: `base_projection * multiplier` exactly once.

The existing R output can be supported as a separate explicit mode where `GB_Projection` is used directly. It must not also multiply by `multiplier`. A field named `3D Proj.` is base data according to `Projections/GameBlazers.Rmd:131-135`; `GB_Projection` is adjusted data.

Reject or flag a row when the chosen projection field is absent, non-numeric, or unmatched. Do not use the golf fallback behavior of silently changing invalid multiplier to 1 or salary to 0.

### Infeasible rosters

A contest should return a structured, user-facing infeasible result when no assignment satisfies all slots and the cap. At minimum show:

- contest name;
- required slot count;
- salary cap;
- reason category: schema error, no eligible card for a slot, duplicate-athlete conflict, or no cap-feasible assignment; and
- no partial lineup.

This is different from a valid optimum with unused cap. A greedy failure must never be reported as infeasibility.

### Required v1 versus later quality of life

**Required v1:**

- existing Flask deployment boundary;
- validated roster/projection upload flow;
- Spark, Scorcher, Wildfire, Inferno, and the provisional Flamethrower configuration;
- exact slot-aware optimization;
- strict salary cap;
- multiplier applied exactly once under an explicit projection contract;
- one-athlete uniqueness;
- no partial lineups;
- clear infeasibility output;
- one selected lineup with slot labels and salary/points totals.

**Later quality of life:**

- card exclusion and re-solve;
- downloadable CSV/JSON result;
- multiple lineup generation with controlled uniqueness/exposure rules;
- status/team/game-window filters;
- viability/ceiling metrics based on the actual eligible pool;
- stable card/athlete IDs from a future trusted export;
- saved sessions and richer UI.

## 8. Recommended implementation sequence

This is a proposed sequence only; no implementation was performed.

1. **Lock the v1 input contract.** Decide whether the first football UI consumes raw base projections plus a roster CSV, already-joined `GB_Projection` rows, or two explicit modes. Default recommendation: preserve the golf two-upload workflow with raw base projections and card roster data.
2. **Add a normalization boundary in the existing Flask app.** Accept documented aliases for name/multiplier/salary, parse numeric fields strictly, preserve original row numbers, generate synthetic row IDs, normalize athlete keys, and report unmatched/malformed rows.
3. **Choose the adjusted-projection mode.** Compute `base * multiplier` once for raw projections; use existing `GB_Projection` directly for pre-adjusted files. Add a test that catches double multiplication.
4. **Represent contest slots explicitly.** Add the five contest configurations, including Flamethrower as provisional, and make Inferno's eight slots explicit rather than relying on a dictionary sum.
5. **Replace the greedy loop with an exact solver.** Prefer a small PuLP assignment model using the already-declared dependency, or implement equivalent slot-aware branch-and-bound. Include athlete-group uniqueness in the model, not as a post-processing filter.
6. **Make infeasibility explicit.** Do not append partial lineups, do not silently break, and distinguish bad input from a valid-but-infeasible roster.
7. **Render one explainable result.** Include contest, slot, player, source card row ID/display metadata, position, multiplier, salary, adjusted projection, total salary, remaining cap, and total projection.
8. **Add focused correctness tests before UI polish.** At minimum cover: a greedy counterexample where the global optimum is not the top player at every slot; a cheaper alternative needed under cap; duplicate cards for one athlete; Flex versus fixed-position competition; QB in Superflex; Inferno eight-player count; missing required position; and no cap-feasible lineup.
9. **Manually exercise the existing Flask upload and result routes with copied/in-memory representative data.** Do not overwrite the canonical uploads or databases. Verify both the 41-row and larger 129-row schemas, including missing `NA` projection rows and exact duplicate rows.
10. **Only after correctness is established, decide on exclusions/downloads.** These are useful but not necessary to prove v1 optimization correctness.

No framework rewrite, database migration, or marketplace integration is necessary for this sequence.

## 9. Decisions still requiring the user

These are the few decisions not resolvable from source/data. Each has a provisional default.

1. **Raw two-file inputs or pre-joined football CSV for v1?**
   - **Why it matters:** the golf page expects two files and raw projections, while the repository's usable football files already contain `GB_Projection`.
   - **Provisional default:** reuse the golf two-upload workflow; projection upload contains a clearly named base projection, roster upload supplies card multiplier/salary. Add pre-joined support later or as an explicitly labeled mode.

2. **What should happen to exact duplicate rows when no card ID is present?**
   - **Why it matters:** the raw and joined samples contain repeated same-name and repeated same-attribute rows, but the CSV cannot tell whether an exact repeat is two cards or an export duplicate.
   - **Provisional default:** collapse exact duplicates for optimization, retain source row numbers for diagnostics, and enforce one normalized athlete regardless.

3. **Should non-Active statuses be eligible?**
   - **Why it matters:** the data includes `Injured Reserve` and `Practice Squad`, while current code ignores status and the confirmed rules do not specify eligibility.
   - **Provisional default:** only include rows with `status == Active` (and flag rows excluded for status) unless the product explicitly wants all owned cards.

4. **Is Flamethrower part of the first shipped contest set, and is `$52,000` final?**
   - **Why it matters:** the user supplied the rule as provisional, and the current code has no Flamethrower entry.
   - **Provisional default:** include it behind the same configuration mechanism with the supplied `$52,000` cap, clearly labeled provisional so the cap can be changed without solver changes.

5. **Should v1 retain golf-style card exclusions?**
   - **Why it matters:** golf has card-level exclusion and automatic re-solving, but football's simplest correct flow does not require it.
   - **Provisional default:** defer exclusions until the exact one-lineup path is correct; if retained, exclude synthetic card rows before solving and display the excluded row identity.

6. **What canonical name source should resolve future projection-name variants?**
   - **Why it matters:** there are punctuation/suffix-sensitive names and no stable IDs.
   - **Provisional default:** trim/case-fold plus a reviewed explicit alias table; do not fuzzy-match silently.

## 10. Evidence appendix with file/line references

### Golf optimizer

- `dfs_optimizer.html:5-10` — static HTML and CDN dependencies.
- `dfs_optimizer.html:16` — fixed six-player UI text.
- `dfs_optimizer.html:28-57` — two file inputs, salary control, optimize button.
- `dfs_optimizer.html:81-105` — result totals and table columns.
- `dfs_optimizer.html:123-134` — state and golf-specific alias map.
- `dfs_optimizer.html:150-160` — salary-change, optimize, clear-exclusion handlers.
- `dfs_optimizer.html:163-185` — PapaParse upload flow and missing validation/error handling.
- `dfs_optimizer.html:188-229` — projection map, aliases, roster merge, card object, multiplier calculation.
- `dfs_optimizer.html:232-309` — separate six-item theoretical DP and its projection-salary assumptions.
- `dfs_optimizer.html:311-367` — grouped exact backtracking solver, cap checks, skip branch, failure behavior.
- `dfs_optimizer.html:383-430` — result rendering, totals, viability calculation.
- `dfs_optimizer.html:436-470` — card exclusion/re-inclusion behavior.

### Football optimizer

- `lineup_optimizer/app.py:1-6` — Flask/Werkzeug/pandas runtime imports.
- `lineup_optimizer/app.py:10-15` — contest configurations; no Flamethrower; Inferno totals eight.
- `lineup_optimizer/app.py:18-25` — upload directory and CSV extension rule.
- `lineup_optimizer/app.py:28-72` — home, upload, process, and unchanged CSV copy flow.
- `lineup_optimizer/app.py:74-76` — unused `combinations` and PuLP imports.
- `lineup_optimizer/app.py:78-94` — lineups route and contest selection.
- `lineup_optimizer/app.py:96-121` — greedy slot loop, candidate selection, row-index removal.
- `lineup_optimizer/app.py:123-141` — cap append behavior, repeated disjoint lineup loop, partial-lineup behavior.
- `lineup_optimizer/app.py:142-154` — raw HTML output and totals.
- `lineup_optimizer/app.py:173-177` — PORT/host deployment behavior.
- `lineup_optimizer/newapp.py:10-15` — duplicate contest configuration.
- `lineup_optimizer/newapp.py:76-92` — alternate lineups route and contest selection.
- `lineup_optimizer/newapp.py:94-125` — greedy selection, candidate-count check, stale-batch duplicate behavior.
- `lineup_optimizer/newapp.py:127-141` — cap check and silent stop on `ValueError`.
- `lineup_optimizer/newapp.py:149-161` — alternate raw HTML output.
- `lineup_optimizer/newapp.py:178-179` — debug development-server entry point.
- `lineup_optimizer/requirements.txt:9` — PuLP 2.9.0 declaration.
- `lineup_optimizer/Procfile:1` — deployed entry point is `python3 app.py`.
- `lineup_optimizer/Test.py:1-6` — scratch script, not an automated test suite.

### Projection generation and roster analyzer boundary

- `Projections/GameBlazers.Rmd:13-16` — external weekly QB/RB/WR/TE projection inputs.
- `Projections/GameBlazers.Rmd:21-24` — projection name suffix stripping.
- `Projections/GameBlazers.Rmd:35-40` — roster input and retained football fields.
- `Projections/GameBlazers.Rmd:59-104` — bye filtering, active roster, position splits, and `Player` rename.
- `Projections/GameBlazers.Rmd:111-127` — position-specific left joins by player name.
- `Projections/GameBlazers.Rmd:131-135` — multiplier-adjusted `GB_Projection`, floor, and ceiling.
- `Projections/GameBlazers.Rmd:141` — generated output filename.
- `GB_roster_analyzer/app.py:240-248` — lineup optimizer is only a placeholder blueprint.
- `GB_roster_analyzer/templates/lineup_optimizer_placeholder.html:1-158` — placeholder UI, no optimizer invocation.

### Actual data evidence

- `data/raw/My_roster.csv:1` — raw roster schema; representative row `:3` shows `Jayden Daniels,WAS,QB,1.3,9750`.
- `data/raw/My_roster.csv:2-12` — representative raw names, positions, multipliers, salaries, statuses, and dates.
- `data/raw/My_roster.csv:60-70` — repeated card/name examples including `Ladd McConkey`, `JuJu Smith-Schuster`, `Jameson Williams`, and an injured-reserve row.
- `data/processed/updated_roster.csv:1` — existing joined 15-column schema.
- `data/processed/updated_roster.csv:2-8` — representative adjusted projections and repeated `Russell Wilson` row.
- `data/processed/updated_roster.csv:19`, `:30`, `:45`, `:86` — missing projection rows identified by read-only CSV inspection.
- `lineup_optimizer/uploads/active_roster_shyam_copy.csv:1-8` — larger joined schema and representative values.
- `lineup_optimizer/uploads/active_roster_shyam_copy.csv:17-19`, `:50-53`, `:88-90`, `:122-125` — duplicate and missing-projection examples.
- `lineup_optimizer/uploads/active_roster_jaz_copy.csv:1` — smaller joined schema; the file contains 41 rows with four football positions.
- `lineup_optimizer/uploads/processed_roster.csv:1` — exact schema consumed by the Flask app.

### Read-only verification performed

- Parsed `lineup_optimizer/app.py`, `lineup_optimizer/newapp.py`, and `GB_roster_analyzer/app.py` with Python `ast.parse`/`compile`; all passed syntax compilation.
- Extracted and compiled the inline JavaScript from `dfs_optimizer.html` with Node; it passed syntax compilation.
- Enumerated and summarized all repository CSV/TSV files with the Python standard library because the system Python environment did not have pandas installed. No packages were installed.
- Inspected nested Git status only; no source, CSV, database, dependency, or existing project file was modified. The only intended new artifact from this discovery is this report.
