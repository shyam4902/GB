# `GameBlazers/` Inspection Notes

**Inspection date:** 2026-08-13  
**Method:** Read-only inventory, SHA-256 comparison, text/CSV/JSON/HTML/XML inspection, and OCR of image/PDF artifacts.  
**Scope:** The entire `GameBlazers/` folder, compared against the rest of the repository while excluding `GameBlazers/` and the previously inspected `GB2/` archive from the external duplicate scan.

## Executive conclusion

`GameBlazers/` is a large historical working archive, not a single application and not a folder of all duplicates. It contains **121 non-`.DS_Store` files**:

- 46 CSV files;
- 32 HTML files;
- 22 PNG screenshots;
- 9 JPG screenshots;
- 7 JSON saved-lineup files;
- 3 PDFs;
- 1 plain-text roster export; and
- 1 XLSX projection workbook.

Only **three files are exact duplicates of files elsewhere in the repository**. There are also several duplicate groups within `GameBlazers/` itself. Most remaining files are historical snapshots, derived exports, screenshots, generated analysis, or successive optimizer prototypes.

The most valuable new material is:

1. a scoring reference with explicit football scoring rules;
2. contest-detail and payout screenshots showing historical salary caps, 50% minimum salary usage, entry limits, and prize schedules;
3. a July 31, 2024 Terms of Service document describing Items, Free-to-Play/Pay-to-Play contests, marketplace use, eligibility, and restrictions on automated access/copying;
4. projection sheets for Weeks 14, 15, and 17 plus an Excel workbook for Week 14;
5. many roster snapshots from different users and dates;
6. a large sequence of manual/browser optimizer prototypes with progressively richer lineup-management features; and
7. saved lineup state showing the prototype's contest-keyed, slot-indexed JSON format.

These findings strengthen the project model but remain historical evidence. They do not establish the current 2026 product rules.

---

## 1. Exact duplicate audit

### 1.1 Exact duplicates outside `GameBlazers/`

| File in `GameBlazers/` | Exact repository duplicate |
|---|---|
| `rosters/My_roster.csv` | `data/raw/My_roster.csv` |
| `rosters/active_roster_jaz copy.csv` | `lineup_optimizer/uploads/active_roster_jaz_copy.csv` |
| `rosters/active_roster_shyam copy.csv` | `lineup_optimizer/uploads/active_roster_shyam_copy.csv` |

The comparison used file-content SHA-256 hashes, so differences in filenames, capitalization, or directory names do not affect the result.

### 1.2 Duplicate groups inside `GameBlazers/`

| Duplicate group | Notes |
|---|---|
| `terms.pdf` and `terms_GB.pdf` | Exact copies of the same 16-page Terms of Service document |
| `lineup optimizer/lineup_optimizer_standalone (5).html` through `(9).html` | Five exact copies of the same standalone optimizer version |
| `lineup optimizer/lineup_optimizer_standalone (3).html` and `(4).html` | Exact copies of each other, but a different version from `(5)`–`(9)` |
| `lineup optimizer/lineup_builder (1).html` and `(2).html` | Exact copies of each other |

The remaining files were not exact content duplicates in the tested repository scope. Conceptual similarity, shared code ancestry, or a derived file with a different output does not count as an exact duplicate.

---

## 2. Legal/rules/reference documents

### 2.1 `terms.pdf` / `terms_GB.pdf`

These are exact copies. OCR identifies the document as:

- **GameBlazers Terms of Service**;
- **Last Modified: July 31, 2024**;
- 16 pages; and
- issued by GameBlazers Acquisition, LLC, a subsidiary of SportsHub Holdings, LLC.

Important statements visible in the document:

- GameBlazers provides both **Free-to-Play (FTP)** and **Pay-to-Play (PTP)** fantasy sports contests.
- Users must generally be U.S. citizens/residents and at least 18 or the applicable age of majority to create an account; PTP participation requires age 21 or older.
- Athlete Items represent professional athletes and certain athletic statistics. Items may be bought, sold, traded, or otherwise acquired and used in FTP or PTP contests.
- Item statistics can be enhanced by multipliers or Boost Items.
- The Marketplace is intended for eligible Item transactions used within the Services; purchases are final and GameBlazers disclaims responsibility for user-to-user transactions and pricing.
- Contests are games of skill judged by the applicable Contest Rules, scoring guidelines, and posted contest details.
- The document prohibits automated interaction, scripts, bots, web scrapers, unreasonable load, unauthorized access, and copying/duplicating or commercially exploiting parts of the Services.
- It also includes a restriction against using the Services for competitive analysis or development of a competing service.

The Terms are important operational context for this repository's marketplace investigation. They are **not** a current contest-rule specification and predate much of the later archive. Any future live-data work must remain authorized, read-only, and consistent with the applicable current terms.

### 2.2 `Scoring info.jpg`

OCR extracted the following football scoring reference:

- 25 passing yards: +1 point, approximately `0.04` points per yard;
- 300+ passing-yard game: +3 points;
- passing touchdown: +4 points;
- interception: `-1` point;
- fumble lost: `-1` point;
- rushing/receiving touchdown: +6 points;
- 10 rushing/receiving yards: +1 point, approximately `0.1` point per yard;
- 100 rushing/receiving-yard game: +3 points;
- reception: +1 point;
- punt/kickoff/field-goal return touchdown: +6 points;
- two-point conversion by pass, run, or catch: +2 points; and
- offensive fumble recovery touchdown: +6 points.

This is stronger project evidence than the older third-party article for the scoring contract, but it is still an archived image rather than a current official API/rules response. The scoring reference should be treated as a dated historical rules snapshot until revalidated.

---

## 3. Contest-detail and payout evidence

### 3.1 Contest detail screenshots

The four files under `contest details/` are screenshots of historical contest-detail pages:

| Screenshot | Historical details visible |
|---|---|
| `Spark details.jpg` | `$1k SPARK`; Contest ID `617`; free entry; `$32,000` salary cap; 50% minimum salary usage (`$16,000`); QB 1, RB 1, WR 1, TE 1, no Flex/Superflex; 203/10,000 entries; 2/2 user entries; opens Nov. 12, 2024 and closes Nov. 17, 2024 |
| `Scorcher details.jpg` | `$3k SCORCHER`; Contest ID `596`; free entry; `$36,750` cap; 50% minimum (`$18,375`); QB 1, RB 1, WR 1, TE 1, Flex 1, no Superflex; 958/10,000 entries; 2/5 user entries; opens Nov. 5, 2024 and closes Nov. 10, 2024 |
| `Wildfire details.jpg` | `$6k WILDFIRE`; Contest ID `615`; free entry; `$48,000` cap; 50% minimum (`$24,000`); QB 1, RB 1, WR 1, TE 1, Flex 2, no Superflex; displayed entrant count is OCR-ambiguous but appears to be a historical contest snapshot; 2/5 user entries; opens Nov. 12, 2024 and closes Nov. 17, 2024 |
| `Inferno Details.jpg` | `$10k INFERNO`; Contest ID `594`; free entry; `$64,000` cap; 50% minimum (`$32,000`); QB 1, RB 2, WR 2, TE 1, Flex 1, Superflex 1; 1,158/10,000 entries; 1/5 user entries; opens Nov. 5, 2024 and closes Nov. 10, 2024 |

These screenshots confirm that the historical contests represented in the app had a **minimum salary-use rule** in addition to a maximum salary cap. The current football Flask optimizer does not enforce the 50% minimum.

They also resolve part of the historical naming ambiguity: **Wildfire** was a real contest name in the archived contest UI, while several browser prototypes use **Volcano** for the same `$48,000`/two-Flex structure. The names should not be silently conflated in a current rules model.

### 3.2 Payout screenshots

The files under `payout tables/` show the historical prize schedules:

- **$1k Spark:** 1st `$250`, 2nd `$100`, 3rd `$50`, 4th `$40`, 5th `$30`, 6–7 `$20`, 8–10 `$10`, 11–20 `$8`, 21–50 `$6`, 51–100 `$4`.
- **$3k Scorcher:** 1st `$600`, 2nd `$300`, 3rd `$150`, 4th `$120`, 5th `$90`, 6th `$60`, 7th `$45`, 8–9 `$30`, 10–20 `$25`, 21–50 `$15`, 51–100 `$9`, 101–200 `$4`.
- **$6k Wildfire:** 1st `$1,200`, 2nd `$600`, 3rd `$300`, 4th `$240`, 5th `$180`, 6th `$120`, 7th `$60`, 8–20 `$30`, 21–50 `$20`, 51–100 `$15`, 101–200 `$10`, 201–312 `$5`.
- **$10k Inferno:** 1st `$3,000`, 2nd `$1,000`, 3rd `$500`, 4th `$400`, 5th `$300`, 6th `$200`, 7th `$100`, 8–9 `$75`, 10 `$50`, 11–20 `$40`, 21–50 `$30`, 51–100 `$20`, 101–200 `$10`, 201–400 `$5`.

The separate `Fantasy_Football_Contest_Likelihoods_with_Payouts.csv` encodes these payout tiers as 47 rows with a contest, rank tier, likelihood, likelihood percentage, and payout. Its likelihood values appear to be rank-share calculations based on the payout ranges, not empirically estimated probabilities of a roster winning.

### 3.3 Historical scoring-threshold screenshots

Three older screenshots contain model output:

- Spark: Top 200 approximately `63.76`, Top 100 `80.05`, Top 50 `101.05`, Top 10 `117.35`, with intervals.
- Scorcher: Top 200 approximately `99.77`, Top 100 `110.44`, Top 75 `116.43`, Top 50 `121.78`, Top 20 `132.36`, Top 10 `138.66`, with intervals.
- Wildfire: Top 312 approximately `123.09`, Top 200 `134.80`, Top 100 `148.12`, Top 50 `160.74`, Top 20 `174.17`, Top 7 `187.78`, with intervals.

A later Wildfire screenshot is nearly identical, with Top 312 `123.08`, Top 200 `134.72`, Top 100 `148.15`, Top 50 `160.76`, Top 20 `174.31`, and Top 7 `187.67`.

These align with the Bayesian analysis artifacts but are historical thresholds, not current guarantees.

---

## 4. Roster and projection data

### 4.1 Roster snapshot families

The `rosters/` directory contains many exports from different users, dates, and processing stages. Common raw export schemas are:

```text
player_name, team, position, multiplier, salary, franchise, tradeable,
expires, card_status, rarity, listed, league, status
```

Two top-level exported-roster files use the alternate source schema:

```text
Player, Positions, Team, Multiplier, Overall, Franchise, Rookie,
Tradeable, Salary, Collection, Status, Expires
```

Observed snapshot sizes include:

- `ExportedRoster_20250928044144.csv`: 249 rows, 156 unique player names, all `Active`;
- `ExportedRoster_20251017093403.csv`: 258 rows, 152 unique player names, all `Active`;
- `lineup optimizer/ExportedRoster_20250914082406.csv`: 242 rows, 151 unique player names, 241 `Active` and one `Listed`;
- `My_roster.csv`: 129 rows, 97 unique names, mostly `Active` with three `Injured Reserve` and one `Practice Squad`;
- `My_roster_2.csv`: 126 rows, 97 unique names, mostly `Active` with four `Injured Reserve` and one `Practice Squad`;
- `playoff_roster.csv`: 165 rows, 117 unique names, 164 `Active` and one `Inactive`; and
- the smallest named user roster has 23 rows, while several others range from roughly 34 to 114 rows.

The source exports show multiplier values from `1.0`/`1` through `1.5`. Duplicate player names are common, which may represent multiple Items/copies, not accidental duplicates. No stable Item ID appears in these CSV schemas.

### 4.2 Derived roster files

Several 98-row files represent an owned roster after game-window/bye processing. Their columns include:

```text
player_name, team, position, multiplier, salary, status,
Game Window, Bye Week
```

Projection-enriched versions add:

```text
Projection, Projection x Multiplier
```

One sample contains 84 unique names across 33 WR, 30 RB, 18 QB, and 17 TE rows, with 91 Active, five Injured Reserve, one Inactive, and one Physically Unable to Perform. The adjusted projection range in the inspected versions is approximately `2.2`–`28.05` or `3.9`–`28.05`, depending on the source snapshot.

The files demonstrate a data-contract transition from raw roster fields to derived game-window and multiplier-adjusted projection fields. They also demonstrate schema drift between lowercase `player_name`/`position` and source-export `Player`/`Positions` conventions.

### 4.3 Projection sheets

`projections sheets/` contains 12 weekly position CSVs:

- QB, RB, WR, and TE for Weeks 14, 15, and 17;
- 3D projection values are populated in every inspected row;
- rows range from 26 to 141 per file; and
- the 3D projection ranges vary by position/week, approximately `0.1` to `22.9`.

Week 14 files include extra DraftKings/FanDuel fields. Weeks 15 and 17 use a shorter schema. Header names also vary:

- `Consensus Proj.` vs. `Consensus`;
- `Projection` vs. `Proj.`; and
- optional blank columns and salary/value columns.

`Projections Sheet.xlsx` contains four named Week 14 sheets—`QB Wk14`, `RB Wk14`, `WR Wk14`, and `TE Wk14`—with shared strings and substantial formatting/empty-row capacity. It is a source workbook rather than a clean normalized data table.

### 4.4 `rosters/Unknown copy.txt`

This is a comma-separated roster export stored with a `.txt` extension. It has the same 13-column lowercase schema as the raw roster CSVs and 48 data rows. It should be detected by content/header rather than filename extension if ingestion is generalized.

### 4.5 Roster PDF

`rosters/GameBlazers - Copy of active_roster_shyam 1.pdf` is a three-page rendered roster/projection report. OCR shows columns for player, position, multiplier, salary, status, game window, SOS, Floor, Consensus, Proj., Ceiling, 3D Proj., GB Projection, GB Floor, and GB Ceiling.

It contains examples such as Kyler Murray, Lamar Jackson, Jayden Daniels, Sam Darnold, Jordan Love, Russell Wilson, and many RB/WR/TE rows. It is useful as a presentation/export artifact, but PDF extraction is lossy and cannot substitute for the underlying CSV.

---

## 5. Bayesian modeling artifact

### `GB_modeling.html`

This is a large generated HTML/R Markdown output dated **December 7, 2024**, authored by Shyam Patel. It is not an exact duplicate of `Contest_Analyzer/GB_modeling.Rmd`, but it contains the same historical contest-analysis family and embedded R code/results.

Embedded data includes:

- Spark Weeks 11–13;
- Scorcher Weeks 8, 10, 11, and 13;
- Wildfire Weeks 11–13; and
- Inferno Weeks 10 and 13.

The embedded Bayesian models use `brms` Gaussian regressions of score thresholds against week number, with 2,000 iterations and four chains. The generated output includes warnings that bulk and tail effective sample sizes are too low and that additional iterations may be needed. This is important: the resulting confidence intervals should not be presented as reliable current probabilities without a larger, cleaner dataset and model diagnostics.

The HTML is a generated report/reference artifact, not a reusable application input.

---

## 6. Browser optimizer archive

The `lineup optimizer/` directory contains **39 files**:

- 31 HTML prototypes;
- 7 JSON saved-lineup files; and
- 1 roster CSV.

### 6.1 Contest configurations found in the prototypes

The prototypes contain several competing historical configurations:

| Name | Salary cap | Slots in prototype |
|---|---:|---|
| Spark | `$32,000` | QB, RB, WR, TE |
| Scorcher | `$36,750` | QB, RB, WR, TE, Flex |
| Volcano | `$48,000` | QB, RB, WR, TE, Flex, Flex |
| Flamethrower | `$60,000` | QB, RB, WR, TE, Flex, Superflex |
| Flex Appeal | `$52,000` | QB, five Flex |
| Inferno | `$64,000` | QB, two RB, two WR, TE, Flex, Superflex |

The richer `GBLv2`, `GBv2.1`, `GBv2.3`, `GBv2.4`, `GBv2.5`, `trying`, `testa`, and `testing` iterations generally use the five-contest set Scorcher, Volcano, Flamethrower, Flex Appeal, and Inferno. Older manual builders often contain only Scorcher, Volcano, and Inferno. `testGB.html` permits up to 150 entries per contest, while other richer versions generally default to six, seven, or eight entries according to contest shape.

The historical contest screenshots in this folder use **Wildfire** rather than Volcano for the `$48,000` two-Flex contest. This is direct evidence of naming/rule drift, not proof that one name is a typo.

### 6.2 Feature progression

Across the prototypes, the archive shows a progression from manual lineup entry toward a richer lineup-management UI:

- CSV upload and player-pool rendering;
- QB/RB/WR/TE filters and search;
- drag-and-drop slot assignment;
- fixed, Flex, and Superflex validation;
- salary totals and projection/floor/ceiling totals;
- team-to-game-window assignment and color coding;
- multiple contest columns and adjustable entry counts;
- player locking and exclusion;
- exposure summaries;
- a player finder;
- save/load lineup JSON;
- editable projected and actual scores; and
- removal/reassignment of players between pool and slots.

The `GBLv2` family calculates adjusted projection, floor, and ceiling as base projection multiplied by the Item multiplier and computes points-per-$1,000 value. It creates IDs from player name, position, and team, which still cannot distinguish multiple Item instances of the same athlete/variant.

`GBupdated.html` uses random IDs for rows, which makes saved identity unstable across reloads. `dfs_lineup_builder_fixed.html` accepts multiple field-name variants and uses `GB_Projection` or `Overall` as points, while other versions derive projections from embedded `PROJECTIONS_DATA`. This reinforces that the archive contains incompatible input contracts.

### 6.3 Standalone optimizer variants

The numbered `lineup_optimizer_standalone` files are earlier browser-only implementations. Their shared behavior includes:

- accepting the alternate source-export CSV schema;
- requiring `Player`, `Positions`, `Salary`, and `Status`;
- filtering to `Status == Active`;
- estimating base projection as `salary / 1000 × 2`;
- multiplying that estimate by the Item multiplier; and
- selecting players greedily by points per salary while filling slot requirements.

The later `(10)`–`(12)` family adds validation and position normalization, but it remains greedy. It rejects duplicate player names within a lineup, but does not perform global backtracking or exact optimization. A failed greedy choice can therefore report no lineup even when a valid lineup exists.

### 6.4 `testGB.html` and external AI call

`testGB.html` adds an `analyzeLineup` feature that constructs a request to Google's Gemini API with Google Search tooling for recent lineup news. The embedded API key variable is empty in the inspected file, so the feature is not configured to run as-is.

This prototype is especially sensitive to privacy, terms, credential, and external-service concerns. It should not be treated as production code or enabled without an explicit, authorized design.

### 6.5 Saved lineup JSON

The seven `dfs-lineups (n).json` files use a common top-level shape:

```json
{
  "lineups": { "scorcher": [], "volcano": [], "flamethrower": [], "flexAppeal": [], "inferno": [] },
  "lockedPlayers": [],
  "excludedPlayers": [],
  "teamWindowAssignments": {}
}
```

Lineups store players under numeric slot keys, for example:

```json
{"players": {"0": "Jayden Daniels_QB_WAS_108", "2": "Terry McLaurin_WR_WAS_229"}}
```

Several saved lineups are partial, and the suffixes in player references appear to be generated row/instance identifiers. The files are UI session snapshots, not proof that every saved lineup was valid under the contest rules.

The team-window assignment object uses NFL team abbreviations and maps them to integer windows. This is useful evidence that the optimizer was intended to manage game timing/exposure, not merely maximize one static lineup.

---

## 7. Image archive beyond contest rules

The remaining screenshots are mostly historical app captures, pack/set screens, leaderboard/lineup results, and market/collection views.

Notable OCR findings include:

- `IMG_1073.PNG`–`IMG_1078.PNG`: historical `$5k INFERNO PLAYOFFS` and `$5k SCORCHER PLAYOFFS` lineup/leaderboard screens, showing ranked scores, Item multipliers, salaries, and slot assignments.
- `Screenshot 2025-09-21 at 4.11.53 AM.png` and `Screenshot 2025-09-22 at 10.29.18 PM.png`: saved results with rank, winnings, total points, player scores, multipliers, and salaries.
- September 2025 screenshots: “2X WR (UNTRADEABLE)” collection/set views with multiplier bands and players.
- September 27, November 14, December 25, and February 8 screenshots: Epic, Rare, and other pack-opening or collection views, with player ratings/multipliers and team/position labels.

These screenshots provide historical UX and Item/pack vocabulary but are not normalized data. OCR errors are present, and no stable card IDs can be safely recovered from the images alone.

---

## 8. Important new engineering implications

1. **Minimum salary usage is a missing contest constraint.** Historical contest screens explicitly require 50% of the cap to be used. A solver that checks only `salary <= cap` can return invalid historical lineups.
2. **Historical Wildfire and prototype Volcano conflict.** The project needs a contest-version/date model rather than a single global contest-name dictionary.
3. **Scoring is more explicit than the current app suggests.** The scoring image should become a dated test fixture once verified against current rules.
4. **The archive contains multiple projection contracts.** Inputs include raw `3D Proj.`, `Projection`, embedded projection maps, `Projection x Multiplier`, `GB_Projection`, and salary-derived estimates.
5. **Status filtering is inconsistent.** Some prototypes require `Active`, while roster snapshots contain Injured Reserve, Inactive, Suspended, Practice Squad, and Physically Unable to Perform states.
6. **Identity is still unstable.** Some prototypes use name/team/position IDs, some random IDs, and saved JSON contains generated suffixes. None provide a confirmed stable Item ID.
7. **The manual UI has more product ideas than the Flask app.** Window assignments, lock/exclude, exposure, score editing, and saved sessions are not represented in the current deployed optimizer.
8. **The saved state is not a solver output contract.** It stores mutable UI state and may contain partial entries; it should not be used as a source of truth for lineup validity.
9. **Generated artifacts need provenance.** The HTML report, PDFs, screenshots, derived CSVs, and JSON files should retain source date/version metadata if used in future analysis.
10. **Marketplace/data collection needs extra legal caution.** The archived Terms explicitly restrict automated access, scraping, copying, and competitive analysis; only authorized, read-only workflows should be considered.

---

## 9. Recommended classification of the folder

| Sub-area | Recommended treatment |
|---|---|
| Raw roster exports | Historical fixtures/examples; keep dates and owner/context where known |
| Derived roster/projection CSVs | Pipeline artifacts; useful for schema tests but not canonical current data |
| Projection sheets/XLSX | Historical projection inputs; normalize headers before reuse |
| Contest screenshots/payouts/scoring | Dated rules evidence; use to design versioned tests, not current production rules |
| Terms PDFs | Legal/reference documents; preserve but do not treat as current product documentation |
| `GB_modeling.html` | Generated historical analysis; archive with its source date and warnings |
| Optimizer HTML prototypes | Archive or select a single baseline; do not assume the newest filename is correct |
| Saved JSON files | UI-session examples; do not treat as validated lineups |
| Pack/leaderboard screenshots | Product/UX evidence; OCR only as an aid, not a canonical dataset |

## Overall conclusion

`GameBlazers/` is a valuable historical evidence archive with substantial duplication by lineage, but only three exact duplicates outside the folder. It adds meaningful facts to the project bible—especially scoring, minimum salary usage, dated contest structures, payout schedules, and the breadth of optimizer UI experiments—while also making the repository's schema/rule drift more apparent.

No source files in `GameBlazers/` were modified during this inspection.
