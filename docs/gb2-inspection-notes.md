# GB2 Inspection Notes

I inspected all 9 files in `GB2/` read-only.

## File-by-file findings

| File | Classification | What it contains |
|---|---|---|
| `GameBlazers.Rmd` | Exact duplicate | Same as `Projections/GameBlazers.Rmd` |
| `GameBlazers (1).Rmd` | Exact duplicate | Also same as `Projections/GameBlazers.Rmd` |
| `app (2).py` | Exact duplicate | Same as `lineup_optimizer/app.py` |
| `GB - Project Summary & Development Log.md` | Unique historical project notes | Detailed roster valuation history, user market observations, rarity floors, sets, contract extensions, Franchise behavior, market spikes, and old UI/development decisions |
| `GameBlazers Roster Analyzer README.md` | Unique but partly stale documentation | Older roster analyzer setup and behavior; still useful for historical context, but it describes the former price-per-game valuation approach rather than the current percentile-based logic |
| `fantasy-market-analysis.md` | Unique analysis document | A December 2025 NFL “buy/sell” simulation covering 33 players, projected rating changes, injuries, rookies, and market catalysts. It is not directly tied to GameBlazers Item salary/multiplier data and has no reproducible source dataset |
| `fantasyvalues.json` | Unique external fantasy-football dataset | 199 ranked NFL players with QB/RB/WR/TE values, rankings, tiers, trends, and external IDs from sources such as Sleeper, ESPN, MFL, and Fleaflicker |
| `lineup_optimizer_standalone.html` | Unique older optimizer prototype | Browser-only optimizer with six historical contest configurations, status filtering, salary-based projection estimation, and greedy generation of three sequential lineups |
| `Football data.twb` | Unique unrelated Tableau workbook | Tableau analysis of 2021 NFL play-by-play data, not GameBlazers data |

## Important new information

### Historical GameBlazers market notes

The project summary contains useful historical user knowledge that was not fully represented in the current project documentation:

- estimated player base of roughly 1,500–3,000 users;
- approximately 50–60 highly engaged “power users”;
- fewer than 5–10 users actively trying to profit from market trading;
- sets reportedly occurring about twice per week and lasting around a week;
- temporary value spikes before primetime games;
- price-per-game estimated to influence only around 30–40% of total value;
- rarity floors of Common `$0.50`, Rare `$1`, Epic `$4`, and Legendary `$10`;
- Franchise and tradeability behavior depending partly on how the Franchise status was acquired.

These should be treated as **historical user/project notes**, not verified current official rules. Some details conflict or are more specific than the current app listing—for example, the old notes emphasize three-month extensions while the current app listing describes one-, three-, and six-month extensions.

### Older optimizer contest vocabulary

The standalone HTML reveals another historical contest configuration:

- Spark — `$32,000`
- Scorcher — `$36,750`
- Volcano — `$48,000`
- Flamethrower — `$60,000`
- Flex Appeal — `$52,000`
- Inferno — `$64,000`

This differs from the current Flask app, which uses Wildfire instead of Volcano and does not include Flex Appeal or Flamethrower. This confirms that contest names and rules have changed across prototypes and should not be treated as settled without checking current in-app rules.

The standalone optimizer is also clearly heuristic rather than exact:

- estimates projection as `salary / 1000 × 2 × multiplier`;
- filters to `Status == Active`;
- greedily fills slots;
- generates three lineups by removing selected player names;
- has no backtracking, persistence, download, or server;
- uses a different CSV schema from the current optimizer.

### `fantasyvalues.json`

This is not a GameBlazers Item dataset. It contains:

- 199 unique NFL players;
- 31 QB, 67 RB, 76 WR, and 25 TE;
- overall ranks 1–199;
- redraft/dynasty-style values;
- 30-day trends;
- external fantasy-platform IDs.

It has no GameBlazers-specific multiplier, salary, rarity, expiration, Franchise status, or Item ID fields. It could be useful as an external player-strength reference, but it should not be used directly for GameBlazers valuation or lineup optimization.

### Tableau workbook

`Football data.twb` is an older Tableau workbook built with Tableau 2022.4 on Mac. It references:

```text
/Users/shyampatel/Downloads/R studio files/pbp-2021.csv
```

It contains five worksheets and one dashboard focused on:

- average yards to go on third down;
- average yards gained on third down;
- first downs by down;
- pass/rush/first-down breakdowns;
- play type and down analysis.

It does not contain GameBlazers-specific fields or concepts and appears to be a separate NFL analytics artifact.

## Overall conclusion

`GB2/` is a mixture of:

1. **three confirmed duplicates;**
2. **older GameBlazers roster/market documentation;**
3. **an older optimizer prototype;**
4. **an unrelated external fantasy-value dataset;** and
5. **an unrelated Tableau NFL play-by-play workbook.**

The most valuable new material is the historical market/development log and the older optimizer configuration. I did not modify any files or update the project bible yet.
