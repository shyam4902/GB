# GameBlazers: Game and Project Bible

**Status:** Working source-of-truth overview  
**Last reviewed:** 2026-08-13  
**Primary audience:** Future agents, developers, analysts, and anyone joining this project

> This document synthesizes the GameBlazers game, the project in this repository, and the conclusions that can reasonably be drawn from both. It is not an official GameBlazers rules document. Details are labeled when they come from the current official site/app listing, this repository's code/data, historical project notes, or an inference.

---

## 1. The short version

GameBlazers is a fantasy sports game that combines **daily fantasy sports**, **collectible player Items**, and a **franchise-style marketplace economy**.

A player does not simply choose any athlete from a universal DFS player pool. Instead, the player builds an Inventory of GameBlazers Items. An Item represents a real football or golf athlete and carries game-specific properties such as a scoring multiplier, salary, rarity, contract expiration, and sometimes a permanent Franchise status. The player then uses eligible Items to assemble lineups for weekly contests. Those Items score according to the athlete's real-world performance, adjusted by the Item's multiplier. The player competes against other users for prizes, while also managing the ownership, expiration, utility, and resale value of the Inventory.

The central strategic tension is:

> **The best Item is not necessarily the Item with the highest raw projection. It is the Item that produces the best contest result while fitting the salary cap, lineup rules, contract window, ownership constraints, and the player's broader Inventory strategy.**

This repository exists because that game creates several analysis problems:

1. **Projection:** What are the underlying real-world player projections for a given slate or week?
2. **Multiplier adjustment:** What does a particular Item's multiplier do to that projection?
3. **Lineup optimization:** Which owned Items form the highest-scoring valid lineup under a contest's rules and salary cap?
4. **Contest strategy:** What scores have historically been needed to reach different payout tiers?
5. **Item valuation:** What might an Item be worth based on historical marketplace sales, rarity, multiplier, remaining usable games, and future contest utility?
6. **Data access:** Can current marketplace and sales information be collected through an authorized, stable source?

The project is therefore not one finished application. It is a collection of R Markdown analyses, Flask prototypes, browser experiments, CSV pipelines, SQLite data, and marketplace-investigation code that are gradually converging on a more complete GameBlazers analysis toolkit.

---

## 2. What GameBlazers is

### 2.1 The player-facing concept

The current official GameBlazers website describes the product as a free-to-play fantasy sports app focused on Football and Golf. Users build lineups from real players, compete in weekly contests, and can win real money. Its core promotional loop is:

- collect or acquire player Items;
- put those Items into lineups;
- watch real games produce fantasy points;
- compete in contests;
- receive prizes or other rewards; and
- use packs, the Marketplace, modifiers, and progression systems to improve the Inventory.

The official Football page describes three especially important activities:

- **Rip Packs & Collect:** acquire Items through packs or the Marketplace.
- **Build Your Roster:** create contest lineups from the Inventory.
- **Win Big Each Week:** compete for weekly cash prizes.

The current Google Play listing adds the broader game framing: Items can be used in contests, Roster Upgrade Challenges, or the Marketplace; users can earn progression rewards through the GB Pass and MiniGames; and modifiers can improve Items.

### 2.2 What makes it different from ordinary DFS

Traditional DFS generally gives every user access to the same player pool and asks them to build a lineup under a salary cap. GameBlazers adds an ownership layer:

- each user has a different Inventory;
- the user's available athletes depend on what they own or acquire;
- Items can have different multipliers and economic attributes;
- an Item has a finite contract life unless it is extended or Franchise-tagged;
- Items can be bought and sold; and
- the same Item's value has both **contest utility** and **market value**.

This makes GameBlazers resemble a combination of:

- a fantasy football or fantasy golf contest platform;
- a collectible-card or ultimate-team game;
- a light franchise/roster-management game; and
- a player-driven marketplace.

The closest project-level mental model is **DFS with an owned, expiring, tradable player-card inventory**.

### 2.3 Current scope and changing details

The official website currently presents both Football and Golf. The repository is heavily focused on NFL Football, although `dfs_optimizer.html` appears to be a golf-oriented optimizer experiment and the root README refers to both fantasy football contests and a golf optimizer.

GameBlazers' product messaging and contest availability can change by season, sport, jurisdiction, and app release. A statement in an older article, a checked-in contest configuration, and the current app may not represent the same moment in the product's history. For implementation work, current in-app rules should take precedence over this document's historical notes.

---

## 3. The core game loop

```text
Acquire Items
    ↓
Build and manage an Inventory
    ↓
Check eligibility, expiration, salary, and contest rules
    ↓
Build a lineup from owned Items
    ↓
Real-world athlete performance becomes fantasy points
    ↓
Apply each Item's multiplier
    ↓
Compete in a weekly contest
    ↓
Earn prizes, credits, XP, packs, or market value
    ↓
Buy, sell, upgrade, extend, or optimize the Inventory
```

A user is simultaneously making two decisions:

1. **Contest decision:** Which lineup maximizes expected contest performance?
2. **Inventory decision:** Should an Item be used now, saved for another contest, upgraded, extended, sold, or kept as a long-term Franchise asset?

This is why a card that is not optimal for one slate may still be valuable. It may have more remaining games, a better multiplier, better rarity, more contest flexibility, or stronger resale value than its immediate projection suggests.

---

## 4. Player Items and the Inventory

### 4.1 What an Item represents

An Item is the game's unit of player ownership. It is associated with a real athlete and normally includes some combination of:

- player name;
- position;
- team;
- scoring multiplier;
- salary used in contests;
- rarity;
- expiration or contract date;
- Franchise status;
- tradeability/listing status;
- rookie or collection metadata; and
- an internal card, player, or listing identifier.

The repository's raw roster export uses fields including:

```text
player_name, team, position, multiplier, salary, franchise,
tradeable, expires, card_status, rarity, listed, league, status
```

The exact exported schema may change. The names above are the schema observed in the checked-in data, not a guaranteed future API contract.

### 4.2 Multipliers

The multiplier is the most important contest-facing Item attribute in this project. If a real-world projection is `P` and the Item multiplier is `M`, the intended adjusted projection is:

```text
adjusted_projection = P × M
```

For example, a player projected for 10 fantasy points with a 1.5x Item would be projected for 15 GameBlazers points, assuming the scoring model applies the multiplier directly.

The checked-in football data contains multipliers from `1.0` through `1.5`. The current Google Play description also documents boosts from 1.0x through 1.4x, including the example of using a 1.4x boost to bring an existing 1.4x Item to a 1.5x multiplier.

A multiplier is not free value. Higher-multiplier Items generally have higher salaries and may have different rarity and market characteristics. The optimizer must therefore maximize projected points subject to the salary cap rather than simply selecting the highest multipliers.

### 4.3 Salary

Each Item has a contest salary. A lineup must satisfy the selected contest's maximum salary cap.

The salary appears to be Item-specific rather than simply a universal salary for the athlete. In the repository's observed files, salary varies across Items and is one of the main inputs to lineup optimization.

The strategic effect is similar to ordinary DFS, but the user cannot necessarily buy or select any athlete at any time. The user is optimizing from the subset of Items actually in the Inventory.

### 4.4 Rarity

Rarity indicates how scarce a particular athlete/multiplier combination is in the Item pool. The older 4for4 explanation describes Legendary as the rarest combination of athlete and multiplier on the platform.

Rarity can affect:

- market price;
- collection value;
- perceived scarcity;
- resale liquidity; and
- possibly long-term franchise value.

The current roster analyzer uses the observed rarity categories:

```text
COMMON, RARE, EPIC, LEGENDARY
```

It also applies configurable minimum valuation floors to these categories when calculating suggested prices from historical sales. Those floors are an analysis policy in this repository, not confirmed official GameBlazers pricing rules.

### 4.5 Expiration and contracts

Non-Franchise Items are time-limited. The current Google Play listing says that every Item is valid for one year unless it comes with a Franchise Tag, and that non-Franchised Items can be extended beyond one year. The older 4for4 explanation similarly describes a 12-month expiration from pack opening.

Expiration matters in at least four ways:

1. **Contest eligibility:** an expired Item cannot be used normally.
2. **Remaining utility:** an Item with more remaining game weeks can produce more future contest value.
3. **Marketplace value:** buyers care about how long the Item remains usable.
4. **Valuation normalization:** the same sale price means something different for an Item with one usable game versus one with a full season remaining.

The roster analyzer tries to estimate “Games Remaining” from an expiration date, current processing date, NFL season dates, team, bye weeks, and Franchise status.

### 4.6 Franchise Items

A Franchise Tag makes an Item permanent for the athlete's career according to the current app listing and older explanatory material. In the repository's valuation logic, Franchise Items are treated as having the maximum seasonal game availability rather than a normal expiration date.

Franchise status changes an Item from a short-term consumable asset into something closer to a durable franchise holding. It may be valuable even when the current weekly projection is mediocre because it avoids contract expiration and can remain useful across seasons.

### 4.7 Modifiers and extensions

The official app listing describes several modifiers:

- contract extensions of one, three, or six months;
- the Necromancer, which can revive a previously expired Item for one month;
- boosts that increase an Item's multiplier; and
- the Franchise Tag, which removes the expiration date permanently.

These modifiers create another layer of optimization. The best use of a modifier may depend on:

- the athlete's expected future performance;
- the current multiplier;
- the Item's rarity;
- the remaining contract period;
- projected contest calendars; and
- the likely resale value after modification.

The current repository does not implement a complete modifier optimizer. Modifier information is part of the game model and should be preserved if future exports expose it.

### 4.8 Ownership and one-lineup-per-week behavior

The current Google Play listing states that an Item can only be used in one lineup per week, but a user can own multiple copies of the same Item and use those copies in separate contests during the same week.

This distinction is important:

- **same Item instance:** limited to one lineup per week;
- **multiple owned copies:** may support multiple lineups, subject to the rules and the number of copies owned;
- **same athlete:** not necessarily limited to one contest if distinct Item instances are owned.

The repository's optimizer experiments do not yet model this full weekly inventory accounting. They mostly solve one lineup from a CSV snapshot. A future multi-contest optimizer must represent Item identity, not just player name.

---

## 5. Contests and scoring

### 5.1 General contest model

A contest defines:

- a sport and slate/week;
- required lineup slots;
- eligible positions per slot;
- a salary cap;
- scoring rules;
- an entry/prize structure; and
- a set of eligible Items from each user's Inventory.

The official site describes players earning points from real-world performance every game and every week. The website currently emphasizes free weekly contests, while the app listing and historical materials describe the broader possibility of paid contests and real-cash competition. Availability may depend on current product rules and jurisdiction.

### 5.2 Football scoring model in the project

The repository's exact scoring rules are not fully encoded. The project assumes the source projection files already contain a fantasy projection, including a field called `3D Proj.`. The pipeline then calculates:

```text
GB_Projection = multiplier × 3D Proj.
```

The project should not multiply an already adjusted `GB_Projection` by the multiplier again. This is one of the most important data-contract risks in the repository.

The older 4for4 article describes the game as using PPR scoring with bonuses for 100- and 300-yardage totals, but that source is from 2023 and should not be treated as a current rules reference without verification.

A dated `GameBlazers/Scoring info.jpg` reference provides a more explicit historical scoring snapshot: 25 passing yards per point, a 300+ passing-yard bonus, passing touchdowns worth 4, interceptions and lost fumbles worth -1, rushing/receiving touchdowns worth 6, 10 rushing/receiving yards per point, a 100-yard bonus, receptions worth 1, return touchdowns worth 6, two-point conversions worth 2, and offensive fumble-recovery touchdowns worth 6. This is useful for historical tests but remains an image artifact rather than a current official rules endpoint.

### 5.3 Contest configurations observed in this repository

The active football Flask app currently defines four contests:

| Contest | Required lineup shape in code | Salary cap | Repository status |
|---|---|---:|---|
| Spark | QB 1, RB 1, WR 1, TE 1 | $32,000 | Present in code and historical analysis |
| Scorcher | Spark + Flex 1 | $36,750 | Present in code and historical analysis |
| Wildfire | Spark + Flex 2 | $48,000 | Present in code and historical analysis |
| Inferno | QB 1, RB 2, WR 2, TE 1, Flex 1, Superflex 1 | $64,000 | Present in code and historical analysis; eight total slots |

The repository's optimizer discovery notes also identify a **provisional Flamethrower** configuration, described as Spark plus two Flex slots with a proposed $52,000 cap. It is not present in the current `CONTESTS` dictionary, so it should be treated as an unresolved product/configuration decision rather than an active rule.

Historical contest-detail screenshots in `GameBlazers/contest details/` add an important constraint not enforced by the current Flask optimizer: Spark, Scorcher, Wildfire, and Inferno each displayed a **50% minimum salary-usage requirement** in addition to the maximum salary cap. The screenshots also show those historical contests as free-entry contests with user-entry limits and dated opening/closing windows. This confirms the rule existed at that historical point, but it must be versioned and rechecked before being made universal.

The current optimizer code is not authoritative for current GameBlazers contest rules. It is the implementation state of this project at the time of review.

### 5.4 Flex and Superflex

The project interprets slots as follows:

- fixed QB/RB/WR/TE slot: only that position is eligible;
- Flex: RB, WR, or TE;
- Superflex: QB, RB, WR, or TE.

A correct optimizer must assign a specific Item to a specific slot. It cannot simply choose the top RBs, top WRs, and top Flex players independently, because the same high-value Item may be eligible for multiple slots.

For example, an RB may be eligible for both the fixed RB slot and a Flex slot. The optimizer must decide whether:

- the RB fills the fixed slot and another player fills Flex; or
- another RB fills the fixed slot and the first RB fills Flex.

This is an assignment problem, not a set of independent top-N queries.

### 5.5 Historical payout analysis

`Contest_Analyzer/GB_modeling.Rmd` contains small historical datasets for Spark, Scorcher, Wildfire, and Inferno. It uses Bayesian regressions over week number to estimate points associated with payout tiers such as Top 200, Top 100, Top 50, Top 20, Top 10, and similar ranks.

Observed historical ranges in the checked-in sample include:

| Contest | Historical sample signal |
|---|---|
| Spark | Top 200 roughly 54–66 points; Top 10 roughly 112–119 points |
| Scorcher | Top 200 roughly 89–105; Top 10 roughly 136–154 |
| Wildfire | Top 312 roughly 122–123; Top 7 roughly 179–191 |
| Inferno | Top 400 roughly 146–168; Top 10 roughly 237–247 |

These values are useful as historical context and as a starting point for modeling contest difficulty. They are not guaranteed thresholds. The sample is small, tied to particular weeks, and likely sensitive to slate size, player availability, scoring rules, and the number/quality of entries.

---

## 6. The GameBlazers economy

### 6.1 Packs

Packs are one acquisition path for Items. The official site describes packs as a way to put new Items into the user's Inventory. The current app listing says packs can be purchased in the Shop and earned through gameplay; many can be bought with credits earned from contest results and GB Pass rewards, while all can be purchased with the GameBlazers balance.

Packs introduce uncertainty and scarcity. Their expected value depends on:

- the possible athlete pool;
- multiplier distribution;
- rarity distribution;
- expiration dates;
- the chance of Franchise or other modifiers; and
- the market value of the resulting Items.

The repository does not currently contain a complete pack-odds or expected-value model.

### 6.2 Marketplace

The Marketplace is the secondary economy where users can buy and sell Items. It matters because users do not need to rely only on packs to acquire a desired athlete or multiplier.

Marketplace value may depend on:

- player performance and popularity;
- multiplier;
- salary efficiency;
- rarity;
- remaining expiration time;
- Franchise status;
- collection demand;
- current contest schedule;
- supply and liquidity; and
- whether the Item is immediately useful in the user's Inventory.

The repository contains two generations of marketplace-related code:

1. `market_py/app.py` — an earlier tRPC marketplace fetcher that saves listing information into a `sales_history` SQLite table.
2. `market_py/update.py` — a newer incremental importer aimed at an authenticated sales endpoint and a normalized `marketplace_sales_v2` table.

Marketplace access is not considered fully solved. The public website did not expose a documented public API route during the repository investigation, and the current plan is to use only authorized, read-only observation of the official client or a user-provided export. The project explicitly avoids certificate-pinning bypasses, hidden-endpoint bypasses, scraping, bots, and automated marketplace actions.

### 6.3 Historical sales and valuation

The roster analyzer reads historical sale records from SQLite and groups them by:

```text
player_name, multiplier, rarity
```

It then:

- converts sale prices from cents to dollars;
- applies minimum rarity floors;
- estimates games remaining at the time of sale;
- calculates price per remaining game;
- trims extreme sales when enough samples exist; and
- produces low, medium, and high historical price estimates.

The analyzer combines those estimates with the current uploaded roster to produce suggested prices and an estimated total account value.

This is best understood as a **heuristic historical valuation tool**, not a live appraisal. The output can be distorted by small sample sizes, changing market conditions, stale sales data, expiration differences, and missing card identifiers.

### 6.4 Historical market observations from GB2

`GB2/GB - Project Summary & Development Log.md` preserves historical user/project observations about the market. These are useful hypotheses, but they are not independently verified current platform statistics:

- estimated total player base of roughly 1,500–3,000 users;
- approximately 50–60 highly engaged “power users”;
- fewer than 5–10 users actively attempting to profit from market trading;
- sets reportedly appearing about twice weekly and lasting roughly one week;
- temporary demand spikes before primetime games;
- price per remaining game estimated to explain only about 30–40% of a card's total value; and
- rarity floors observed or assumed as Common `$0.50`, Rare `$1`, Epic `$4`, and Legendary `$10`.

The same notes describe a three-month normal contract extension and tradeability rules that may depend on how a Franchise status was acquired. The current Google Play listing describes one-, three-, and six-month extensions, so the older notes should be treated as a historical snapshot until current in-app behavior is verified.

These observations reinforce that GameBlazers value is not simply projected points divided by games remaining. Rarity floors, sets, contest timing, player demand, expiration, Franchise status, and liquidity can all dominate a simple price-per-game estimate.

### 6.5 GB Pass and MiniGames

The GB Pass is a progression/battle-pass system. Users earn XP through activity and unlock rewards. The official app listing says rewards can include packs, Items, modifiers, credits, contract extensions, and more.

MiniGames, including Pick 'Ems and Player Props according to the app listing, provide additional free ways to earn XP and rewards. They make the overall product broader than a single weekly lineup contest: a user can engage with the app even when they are not actively optimizing a contest lineup.

### 6.6 Roster Upgrade Challenges

Roster Upgrade Challenges, or RUCs, are listed by the current app as another use for Items. They are not implemented or modeled in this repository, but they are relevant to the total Item economy because an Item may have value as a challenge input rather than as a contest lineup piece or marketplace listing.

---

## 7. This repository's project

### 7.1 Project purpose

The repository is trying to turn GameBlazers data into decision support for a user who owns a roster of Items. Its practical questions are:

- Which Items should be used in a particular contest?
- What might each Item be worth?
- How many real-world points are needed to compete for different payout tiers?
- How should player projections be merged with Item-specific multipliers and salaries?
- How can current marketplace data be captured and normalized without relying on an unstable or undocumented interface?

The project is currently more of an analysis lab and prototype suite than a unified production system.

### 7.2 Repository map

| Path | Purpose | Current maturity |
|---|---|---|
| `Projections/GameBlazers.Rmd` | Reads weekly position projection CSVs, filters roster data, handles bye/game-window logic, joins projections to owned Items, and calculates multiplier-adjusted projections | Historical R Markdown pipeline; depends on external `~/Downloads` files |
| `Contest_Analyzer/GB_modeling.Rmd` | Models historical contest payout-tier scores with Bayesian regressions | Historical analysis with small manually entered samples |
| `GB_roster_analyzer/app.py` | Flask app for roster upload, expiration/game counting, historical-sales valuation, sorting, and results display | Main roster analysis web app; not a complete game client |
| `GB_roster_analyzer/gameblazers.db` | SQLite database used by the roster analyzer | Historical sales database |
| `GB_roster_analyzer/templates/` | Roster analyzer UI and a placeholder optimizer page | Existing dark/light UI templates |
| `lineup_optimizer/app.py` | Standalone Flask football optimizer | Declared deployment entry point; currently greedy and incomplete |
| `lineup_optimizer/newapp.py` | Alternate/older football optimizer | Not referenced by the `Procfile`; also greedy |
| `lineup_optimizer/Procfile` | Deployment command | `web: python3 app.py` |
| `lineup_optimizer/uploads/` | Example joined roster/projection CSVs | Local sample inputs and generated copies |
| `dfs_optimizer.html` | Browser-only optimizer experiment | Golf-oriented, six-player exact search with no backend or persistence |
| `market_py/app.py` | Earlier marketplace fetcher and sales-history importer | Experimental; depends on a marketplace response shape |
| `market_py/update.py` | Incremental authenticated marketplace-sales importer | Newer experimental importer with normalized schema and self-test |
| `GB_market/` | SQLite browser project metadata | Opens a `gameblazers.db` database in SQLiteBrowser-style tooling |
| `GB2/` | Historical archive of duplicate scripts, older notes, optimizer experiments, external fantasy data, and an unrelated Tableau workbook | Mixed historical/reference material; not a coherent application and not all files are GameBlazers-specific |
| `GameBlazers/` | Larger historical evidence archive containing dated rules screenshots, scoring/payout references, roster/projection snapshots, generated modeling output, browser optimizer iterations, and saved lineup state | Mixed historical/reference material; contains only three exact duplicates outside the folder and many internal snapshots/variants |
| `README.md` | High-level project description | Describes projections, contest analysis, optimizer, and data folders |
| `STATE.md` | Current investigation state | Says marketplace access discovery is in flight and modernization has not started |
| `optimizer-discovery.md` | Detailed read-only optimizer audit | Most complete technical account of current optimizer behavior and proposed v1 |

### 7.3 Roster/projection data flow

The intended football analysis flow is:

```text
External weekly QB/RB/WR/TE projection CSVs
                    │
                    ├── normalize player names
                    └── retain projection fields
                                  │
Owned roster CSV ── filter position, status, bye teams, dates
        │                         │
        └──── join by player name and position ────┘
                                  │
                    3D Proj. × multiplier
                                  │
                    GB_Projection output CSV
                                  │
                 lineup optimizer / analysis
```

`Projections/GameBlazers.Rmd` currently:

1. reads four position-specific projection files from `~/Downloads`;
2. strips trailing team and position abbreviations from projection player names;
3. reads a roster export;
4. retains player name, position, multiplier, salary, status, and team;
5. marks bye-week teams;
6. maps teams to game windows;
7. removes bye-team rows;
8. joins each position's roster rows to its position-specific projections by `Player`; and
9. calculates `GB_Projection`, `GB_Projection_Floor`, and `GB_Projection_Ceiling` by multiplying the underlying projection fields by the Item multiplier.

The output is written as `active_roster_playoff.csv` in the R Markdown source, although checked-in project files use names such as `updated_roster.csv` and `active_roster_*_copy.csv`.

### 7.4 The roster analyzer

The roster analyzer is the most complete user-facing application in the root project. It accepts a roster CSV, validates core fields, parses expiration dates, estimates remaining games, merges historical sales data, and renders a sortable roster table.

Core fields expected by the analyzer:

```text
player_name, multiplier, expires, rarity
```

Optional or behavior-changing fields include:

```text
franchise, tradeable, team, position, status
```

The analyzer's major concepts are:

- **Games Remaining:** estimated usable games before expiration, adjusted for season boundaries and bye weeks.
- **Historical prices:** low/medium/high estimates from grouped sales.
- **Suggested prices:** historical estimates applied to the current roster, with “not enough sales data” and “untradeable” states.
- **Total account value:** sum of numeric suggested medium prices.
- **Sorting:** by name, suggested price, games remaining, expiration, and rarity.

The `/lineup_optimizer/` route in this app is currently only a placeholder page. It does not call the standalone football optimizer.

### 7.5 The football optimizer

The active deployment entry point is `lineup_optimizer/app.py`. It uploads one already-joined CSV, copies it to `processed_roster.csv`, lets the user select a contest, and returns generated lineup HTML.

The current implementation has important limitations:

- it selects the highest `GB_Projection` candidates independently for each slot;
- it is greedy and does not solve the global salary-constrained assignment problem;
- it can produce partial lineups;
- it removes pandas rows rather than enforcing one real athlete per lineup;
- it does not clearly handle duplicate card rows;
- it does not validate the required schema or projection types;
- it does not enforce a status policy;
- it does not return explicit infeasibility reasons;
- it generates repeated disjoint lineups rather than clearly defining a single optimal lineup workflow; and
- it does not use the PuLP dependency even though PuLP is declared and imported.

`newapp.py` attempts to reject missing positions and cap failures but remains greedy and is not the deployed entry point.

The intended safe v1 direction, documented in `optimizer-discovery.md`, is an exact slot-aware assignment model with:

- one selected Item per slot;
- one use per Item row;
- one use per normalized real athlete unless distinct Item ownership is explicitly modeled;
- a strict salary cap; and
- maximized adjusted projection.

### 7.6 The golf/browser optimizer

`dfs_optimizer.html` is a separate, static browser page. It accepts a projections CSV and a roster CSV, merges them in memory, applies `base_projection × multiplier`, and uses recursive branch-and-bound to find an exact six-player lineup under a configurable salary cap.

It also supports card-level exclusions and re-solves when the salary cap or exclusions change.

This page is useful as a demonstration of an exact-search mindset, but it is not a Football implementation:

- it is hardcoded to six players;
- it has no position or slot model;
- it uses golf-specific names and columns;
- it has no server, persistence, download, or API; and
- its theoretical “absolute max” calculation does not necessarily correspond to the actual uploaded roster.

### 7.7 Marketplace research

Marketplace investigation is deliberately separate from the roster/optimizer work. `STATE.md` says the current phase is access discovery only.

The project has not established a stable public API or documented export. The current plan is:

1. use the official iPhone/iPad app with the user's own account;
2. if practical, observe a short normal read-only marketplace session through a trusted local proxy;
3. redact credentials, tokens, device identifiers, and personal data;
4. record only read-side request hosts, schemas, pagination, timestamps, and stable IDs;
5. avoid purchases, listings, account changes, automation, scraping, and access-control bypasses; and
6. fall back to an app-supported export or user-provided data if live observation is not feasible.

This boundary matters: the project should not treat an experimental endpoint or a historical SQLite file as a guaranteed current marketplace feed.

### 7.8 GB2 archive and newly inspected artifacts

`GB2/` is a mixed historical archive rather than a second complete application. A read-only comparison found nine files:

- `GameBlazers.Rmd` and `GameBlazers (1).Rmd` are both exact duplicates of `Projections/GameBlazers.Rmd`.
- `app (2).py` is an exact duplicate of `lineup_optimizer/app.py`.
- `GB - Project Summary & Development Log.md` contains older roster-analyzer decisions and user-supplied market observations.
- `GameBlazers Roster Analyzer README.md` documents an older version of the roster analyzer, including the former price-per-game valuation approach; it is partly stale relative to the current percentile-based code.
- `lineup_optimizer_standalone.html` is an older browser-only optimizer prototype. It filters for `Status == Active`, expects fields such as `Player`, `Positions`, `Salary`, `Multiplier`, `Team`, and `Overall`, estimates projection as `salary / 1000 × 2 × multiplier`, and greedily generates up to three sequential lineups.
- `fantasyvalues.json` contains 199 ranked NFL players: 31 QB, 67 RB, 76 WR, and 25 TE. It has redraft/dynasty-style values, rankings, trends, tiers, and external fantasy IDs, but no GameBlazers multiplier, salary, rarity, expiration, Franchise, or Item ID fields. It is an external player-value reference, not a GameBlazers Item dataset.
- `Football data.twb` is a Tableau 2022.4 workbook using a 2021 NFL play-by-play file from an external local path. Its five worksheets analyze third-down yards, first downs, pass/rush activity, and play types. It contains no GameBlazers-specific fields and appears unrelated to the Item/contest project.

The standalone optimizer records a different historical contest vocabulary from the active Flask app:

| Historical standalone name | Configuration in the archived prototype |
|---|---|
| Spark | QB, RB, WR, TE; `$32,000` |
| Scorcher | Spark + Flex; `$36,750` |
| Volcano | Spark + two Flex slots; `$48,000` |
| Flamethrower | Spark + Flex + Superflex; `$60,000` |
| Flex Appeal | QB + five Flex slots; `$52,000` |
| Inferno | QB, two RB, two WR, TE, Flex, Superflex; `$64,000` |

This differs from the current Flask configuration, which uses Wildfire rather than Volcano and does not include Flex Appeal or Flamethrower. It is additional evidence that contest names and rules changed across prototypes and must be verified against the current app before implementation.

The detailed inspection record is in `docs/gb2-inspection-notes.md`.

### 7.9 The `GameBlazers/` historical evidence archive

A second read-only inspection of `GameBlazers/` found 121 non-`.DS_Store` files: 46 CSVs, 32 HTML files, 22 PNGs, 9 JPGs, 7 JSON files, 3 PDFs, 1 XLSX workbook, and 1 comma-separated roster export stored as `.txt`. It is an archive of historical work rather than a coherent application.

Exact duplicate findings:

- `GameBlazers/rosters/My_roster.csv` duplicates `data/raw/My_roster.csv`.
- `GameBlazers/rosters/active_roster_jaz copy.csv` duplicates `lineup_optimizer/uploads/active_roster_jaz_copy.csv`.
- `GameBlazers/rosters/active_roster_shyam copy.csv` duplicates `lineup_optimizer/uploads/active_roster_shyam_copy.csv`.
- `terms.pdf` and `terms_GB.pdf` are exact internal copies.
- Several numbered standalone HTML files and two numbered `lineup_builder` files are exact internal copies of one another.

The most important new rules evidence is historical rather than current:

- `Scoring info.jpg` lists explicit football scoring values, including passing/rushing/receiving yardage rates, touchdowns, turnovers, receptions, return scores, conversions, and yardage bonuses.
- Contest screenshots show Spark at `$32,000`, Scorcher at `$36,750`, Wildfire at `$48,000`, and Inferno at `$64,000`.
- Those screenshots show a 50% minimum salary-usage requirement, free entry, dated contest windows, and historical entry limits.
- Payout screenshots show the dated `$1k Spark`, `$3k Scorcher`, `$6k Wildfire`, and `$10k Inferno` prize schedules.
- The archived Terms of Service is dated July 31, 2024 and documents FTP/PTP contests, Athlete Items, multipliers, Marketplace transactions, eligibility restrictions, and prohibitions on automated access, scraping, copying, and competitive analysis. It is legal/reference context, not a current rules API.

The archive contains many roster snapshots, including raw exports with 23–258 rows, duplicate player names, multipliers from 1.0 through 1.5, and statuses such as Active, Injured Reserve, Inactive, Suspended, Practice Squad, and Physically Unable to Perform. Derived 98-row reports add game windows, bye weeks, projections, and `Projection x Multiplier`. The projection archive covers QB/RB/WR/TE sheets for Weeks 14, 15, and 17, with header/schema drift between weeks and extra DraftKings/FanDuel columns in some Week 14 files. `Projections Sheet.xlsx` contains four Week 14 position sheets.

`GB_modeling.html` is a generated December 7, 2024 Bayesian report containing Spark, Scorcher, Wildfire, and Inferno data. Its embedded `brms` output warns that bulk and tail effective sample sizes are too low, so its confidence intervals are historical exploratory results rather than dependable current probabilities.

The 31 browser optimizer HTML files show a progression from manual drag-and-drop builders to richer lineup-management prototypes with team game-window assignment, lock/exclude controls, exposure views, finder/search, editable scores, and save/load behavior. Their input and projection contracts are inconsistent: some use embedded projections multiplied by the Item multiplier, some use `GB_Projection`/`Overall`, and the standalone variants estimate points from salary and multiplier. The configurations repeatedly include Scorcher, Volcano, Flamethrower, Flex Appeal, and Inferno, while the historical contest screenshots use Wildfire for the `$48,000` two-Flex contest. This is additional evidence that contest names and rules must be versioned.

The seven saved JSON files are UI session snapshots keyed by contest name, with numeric slot indexes, generated player references, lock/exclude arrays, and team-window assignments. Several saved entries are partial; they are not a canonical record of valid lineups.

The detailed inspection record is in `docs/gameblazers-folder-inspection-notes.md`.

---

## 8. Data model and important technical assumptions

### 8.1 Two different projection contracts exist

The project currently has two possible input models:

#### Raw projection model

```text
projection file: player + base projection
roster file: player + multiplier + salary
adjusted projection = base projection × multiplier
```

This is the model used conceptually by `dfs_optimizer.html`.

#### Already-joined football model

```text
CSV row: Player + position + multiplier + salary + 3D Proj. + GB_Projection
GB_Projection is already adjusted
```

This is the model used by the checked-in football optimizer files and generated by the R pipeline.

A future system must declare which model it is receiving. Applying the multiplier to an already-adjusted `GB_Projection` would double-count the Item multiplier.

### 8.2 Identity is currently name-based

The R pipeline joins roster and projections by player name after splitting by position. The checked-in CSVs do not expose a stable athlete ID or card ID.

Names include punctuation and suffixes such as:

- `C.J. Stroud`;
- `D'Andre Swift`;
- `J.K. Dobbins`;
- `T.J. Hockenson`;
- `Brian Robinson Jr.`; and
- `Michael Penix Jr.`

The safe current approach is conservative normalization:

1. trim whitespace;
2. case-fold for comparison;
3. preserve the original display name;
4. apply only reviewed, explicit aliases; and
5. use team and position as validation metadata.

Fuzzy matching should not silently merge two athletes. A future authorized data source should provide stable athlete, Item, and listing identifiers.

### 8.3 Duplicate rows are real in the current data

The observed raw and joined CSVs contain repeated player names and repeated attribute combinations. Examples include repeated rows for Russell Wilson, Chuba Hubbard, Ladd McConkey, and other athletes.

This can mean:

- multiple legitimate Item variants;
- duplicate export rows; or
- multiple owned copies of an Item.

Without stable card IDs, the optimizer cannot know which interpretation is correct. At minimum:

- exact duplicate rows should not create an extra athlete in a lineup;
- a synthetic input-row ID should be retained for diagnostics; and
- a future multi-lineup model should distinguish real Item instances from equivalent exported rows.

### 8.4 Status and eligibility are not fully specified

Observed football data includes statuses such as:

- `Active`;
- `Injured Reserve`; and
- `Practice Squad`.

The current optimizer does not enforce a status policy. The roster analyzer preserves status but does not use it as a universal optimizer rule.

Whether a user may use a non-Active owned Item can be a product rule, a contest rule, or a data freshness issue. It should be made explicit rather than inferred from the CSV.

### 8.5 Expiration is not the same as current availability

An Item may have a future expiration date and still be unusable for a particular contest because of:

- a bye week;
- an inactive status;
- a contest-specific eligibility rule;
- a league or sport mismatch;
- a missing projection; or
- an already-consumed weekly usage slot.

Expiration and contest eligibility should be separate fields in a future normalized model.

---

## 9. What the project is trying to become

The most coherent long-term product interpretation is a **GameBlazers decision-support platform** with four connected but separable capabilities:

### 9.1 Inventory intelligence

Answer:

- What Items do I own?
- Which ones are expiring soon?
- How many usable games remain?
- Which Items are Franchise, tradeable, listed, or unavailable?
- What is my estimated account value?

### 9.2 Weekly projection and lineup optimization

Answer:

- What are the current player projections?
- What is each owned Item's adjusted projection?
- Which valid lineup maximizes points under a contest cap?
- What changes if a card is excluded, expires, or is reserved for another contest?

### 9.3 Contest strategy and benchmarking

Answer:

- What score has historically reached a payout tier?
- How difficult is this contest relative to prior weeks?
- What projected score gives the lineup a reasonable chance?
- How much does lineup variance matter versus raw projection?

### 9.4 Marketplace and economic analysis

Answer:

- What have comparable Items sold for?
- How does price vary with multiplier, rarity, expiration, and Franchise status?
- Is it better to use, sell, extend, or upgrade an Item?
- Which missing Item would most improve the user's available lineups?

These capabilities should share a normalized Item model but should not be forced into one large application prematurely. Marketplace ingestion, roster valuation, projection generation, and lineup solving each have different correctness requirements and data freshness assumptions.

---

## 10. Known limitations and risks

### 10.1 Game-rule drift

The official app, official website, older articles, checked-in code, historical contest datasets, and the `GameBlazers/` screenshots represent different moments. Contest names, caps, minimum salary usage, entry rules, scoring, sports, and prize structures can change. The GB2 and GameBlazers archives make this especially clear: one optimizer prototype uses Volcano, Flamethrower, and Flex Appeal, while historical contest screenshots use Wildfire for the same `$48,000` two-Flex shape and the active Flask app uses Wildfire while omitting several prototype contests.

### 10.2 Historical minimum-salary constraint

The dated contest screenshots show a 50% minimum salary-use rule. The current optimizer checks the maximum cap but does not enforce this lower bound. Any solver that uses the historical contest model must support both constraints and must make them contest-version-specific.

### 10.3 Stale projection inputs

The R Markdown pipeline references external files under `~/Downloads`, including week-specific projection sheets. The original source projections are not fully reproduced in the repository, so the pipeline is not currently a self-contained reproducible build.

### 10.4 Double multiplier risk

The same repository contains both base projections and adjusted `GB_Projection` outputs. A new optimizer must make the projection mode explicit and test that the multiplier is applied exactly once.

### 10.5 Name-only joins

Name joins are fragile around punctuation, suffixes, aliases, and spelling changes. They also cannot distinguish duplicate owned copies or separate Item instances.

### 10.6 Historical market data is not live market data

The SQLite database is historical context. It should not be presented as a current price feed, and its sales may have missing identifiers or inconsistent timestamp semantics.

### 10.7 Small historical samples

The contest analyzer uses manually entered samples from a limited number of weeks. Its estimates are useful as a baseline but should not be treated as stable probabilities or current payout guarantees.

### 10.8 Current optimizer correctness

The football optimizer's greedy behavior can miss a better lineup, violate athlete uniqueness, accept partial lineups, or fail to distinguish true infeasibility from a bad greedy choice. This is the highest-priority technical correctness issue in the existing tooling.

### 10.9 Security and operational concerns

The repository contains development-oriented behavior such as:

- hardcoded Flask secret configuration in the roster analyzer;
- debug-mode development launching in the older optimizer;
- shared upload filenames;
- hand-built HTML output; and
- experimental marketplace request code.

These tools should not be treated as production services without configuration, validation, isolation, and authorization work.

---

## 11. Open questions for future work

### Product and rules

1. What are the current official NFL and Golf scoring rules?
2. Which contests are currently active, and are they free, paid, or jurisdiction-dependent?
3. Which contest vocabulary is current: Spark, Scorcher, Wildfire, Volcano, Flamethrower, Flex Appeal, Inferno, or another set of contests?
4. What are the current lineup shapes and salary caps for each active contest family?
5. What exactly does “one lineup per week” mean for every contest type and sport?
6. How are Items treated when the athlete is inactive, traded, on a bye, or no longer in the relevant league?

### Data

7. Is there an authorized current export or stable API response for owned Items and marketplace sales?
8. What are the canonical athlete ID, Item ID, listing ID, and player ID fields?
9. Can the source provide Item-instance ownership so duplicate copies can be modeled correctly?
10. Is `3D Proj.` the official base projection contract, or only a project-specific input field?
11. Are salary and multiplier values static per Item or recalculated by contest/slate?

### Optimization

12. Should the first optimizer return one best lineup or multiple lineups?
13. Should a lineup enforce one normalized athlete or one Item instance, and under what context?
14. Should non-Active Items be excluded automatically or shown with a warning?
15. Should exact duplicate export rows be collapsed?
16. Should the optimizer model reserving Items for multiple contests in the same week?

### Valuation

17. Should the value model use sale price, price per remaining game, contest utility, or a combined estimate?
18. How should Franchise Items be compared with expiring Items?
19. How should low-sample player/multiplier/rarity groups be valued?
20. Should a current marketplace price be separated from a historical fair-value estimate?

---

## 12. Recommended implementation direction

If development resumes, the safest order is:

1. **Define a normalized Item schema** with display fields, athlete identity, Item identity, multiplier, salary, expiration, Franchise status, eligibility, and source metadata.
2. **Make projection mode explicit:** raw base projection plus multiplier, or already-adjusted `GB_Projection`.
3. **Preserve source row and source file metadata** so every optimizer result can be traced back to its input.
4. **Replace the football greedy loop with an exact slot-aware solver** and include salary and athlete/Item constraints in the model.
5. **Return no partial lineups.** Distinguish schema errors, missing eligible positions, duplicate conflicts, and cap infeasibility.
6. **Add focused correctness tests** for Flex/Superflex competition, salary alternatives, duplicate athlete rows, Inferno's eight slots, missing positions, and double multiplier application.
7. **Separate current marketplace snapshots from historical sales.** Store raw responses separately from normalized records and deduplicate by stable listing IDs.
8. **Only then add quality-of-life features** such as card exclusions, multiple lineups, downloads, status filters, schedule filters, and saved sessions.

No framework rewrite or database migration is necessary to prove the core lineup-optimization concept. The main need is a correct data boundary and a correct solver.

---

## 13. Evidence and source notes

### Official/current sources

- [GameBlazers official homepage](https://www.gameblazers.com/) — describes Football and Golf, free-to-play positioning, weekly contests, Items, Packs, MiniGames, GB Pass, Marketplace, and real-money prizes.
- [GameBlazers official Football page](https://www.gameblazers.com/football) — describes football Items, packs, roster building, weekly contests, and prizes.
- [GameBlazers Google Play listing](https://play.google.com/store/apps/details?id=com.sportshubtech.gameblazers.prod&hl=en_US) — current app description reviewed 2026-08-13; documents Items, one-lineup-per-week behavior, expiration, Franchise status, Packs, GB Pass, modifiers, MiniGames, RUCs, age restrictions, and current product messaging.

### Historical/external explanatory source

- [4for4: GameBlazers 101](https://www.4for4.com/2023/w13/gameblazers-101-how-play-and-win-fantasy-footballs-newest-game) — published 2023-11-27; useful for historical explanations of multipliers, rarity, Franchise Items, salary caps, PPR, and early contest/jurisdiction descriptions. It should not be assumed to reflect current rules.

### Repository sources

- `README.md` — high-level project purpose.
- `Projections/GameBlazers.Rmd` — weekly football projection and roster-join pipeline.
- `Contest_Analyzer/GB_modeling.Rmd` — historical contest data and Bayesian payout-tier analysis.
- `GB_roster_analyzer/app.py` — roster upload, expiration/game counting, historical valuation, and results app.
- `lineup_optimizer/app.py` — deployed football optimizer entry point and contest configuration.
- `lineup_optimizer/newapp.py` — alternate/older football optimizer.
- `lineup_optimizer/Procfile` — deployment entry point.
- `dfs_optimizer.html` — browser-only golf-style exact lineup optimizer experiment.
- `market_py/app.py` — earlier marketplace fetch and sales-history importer.
- `market_py/update.py` — newer incremental marketplace-sales importer and normalized schema experiment.
- `STATE.md` — current marketplace-investigation status and safety boundaries.
- `docs/marketplace-investigation-plan.md` — authorized read-only marketplace discovery plan.
- `optimizer-discovery.md` — detailed technical audit of optimizer behavior, CSV schemas, confirmed bugs, and recommended v1 solver design.
- `GB2/GB - Project Summary & Development Log.md` — historical roster-analyzer development log and user/project market observations; useful context but not a current official rules source.
- `GB2/GameBlazers Roster Analyzer README.md` — older roster-analyzer setup and behavior documentation; partly stale.
- `GB2/lineup_optimizer_standalone.html` — archived browser optimizer prototype with historical contest configurations.
- `GB2/fantasyvalues.json` — external 199-player fantasy-value/ranking dataset, not a GameBlazers Item export.
- `GB2/Football data.twb` — unrelated Tableau 2021 NFL play-by-play workbook.
- `docs/gb2-inspection-notes.md` — detailed read-only inspection and duplicate classification for the GB2 archive.
- `GameBlazers/Scoring info.jpg` — dated historical football scoring reference.
- `GameBlazers/contest details/` — dated Spark, Scorcher, Wildfire, and Inferno contest screenshots showing caps, roster shapes, 50% minimum salary use, entry limits, and contest windows.
- `GameBlazers/payout tables/` — dated prize-schedule screenshots for the four historical contest families.
- `GameBlazers/terms.pdf` and `GameBlazers/terms_GB.pdf` — identical July 31, 2024 Terms of Service copies; legal/reference context and automation restrictions, not current product rules.
- `GameBlazers/GB_modeling.html` — generated December 7, 2024 Bayesian contest-threshold report with documented effective-sample-size warnings.
- `GameBlazers/projections sheets/` — historical position projection CSVs for Weeks 14, 15, and 17 plus a Week 14 Excel workbook.
- `GameBlazers/lineup optimizer/` — historical browser optimizer variants and saved JSON session state; useful for feature history and schema discovery, not a canonical solver.
- `docs/gameblazers-folder-inspection-notes.md` — detailed read-only inspection and duplicate classification for the GameBlazers archive.

---

## 14. Final mental model for future agents

When working on this project, think of GameBlazers as five connected layers:

```text
1. Real sports
   NFL/Golf events produce the underlying athlete performance.

2. Fantasy scoring
   Performance becomes fantasy points under GameBlazers' scoring rules.

3. Owned Items
   Each user has a different set of player Items with multipliers, salaries,
   rarity, expiration, Franchise status, and ownership constraints.

4. Contests
   Users assemble valid lineups under slot and salary rules and compete for
   prizes based on the resulting scores.

5. Item economy
   Packs, modifiers, GB Pass rewards, RUCs, expiration, and the Marketplace
   determine how users acquire, improve, value, use, and sell Items.
```

The repository is building analysis tools across those layers. The most important engineering principle is to keep them connected through explicit, traceable data contracts while not confusing a historical project assumption with a current official GameBlazers rule.
