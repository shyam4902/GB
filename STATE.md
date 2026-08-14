# GB Project State

Updated: 2026-08-13

## Shipped recently
- Added `lineup_optimizer/optimizer_core.py`: pure roster/projection parsing, conservative normalization, strict name/position/team matching, eligibility diagnostics, and exact slot-aware assignment.
- Added `lineup_optimizer/test_optimizer_core.py` and `lineup_optimizer/test_optimizer_fixtures.py` with 20 passing tests.
- Added explicit Flex Appeal fixtures and updated projection fixtures with mandatory team fields.
- V1 contests now encode slots plus historical 50% minimums: Spark, Scorcher, Wildfire, Flex Appeal, Flamethrower, Inferno; `Volcano` is an internal Wildfire alias.
- Verified raw projection × multiplier is applied exactly once, variants remain choices, exact visible duplicates collapse, and one normalized athlete cannot repeat.
- Historical Week 15 smoke check: 129 roster rows, 329 projection rows, 120 matched cards, 110 eligible cards; Spark, Scorcher, Wildfire, Flex Appeal, Flamethrower, and Inferno all feasible.
- Added the stateless Flask adapter in `lineup_optimizer/app.py`, a responsive server-rendered template, and focused Flask test-client coverage for the two-upload → contest → result flow. Uploads stay in memory and the selector reads `optimizer_core.CONTESTS`.
- Verified the Flask flow in the project-local `.venv`: 14 Flask client tests, 20 optimizer-core/fixture tests, clean Python compilation, and live Chrome rendering at 1440×900 and 390×844.
- Updated `docs/optimizer-v1-readiness.md`, `fixtures/optimizer_v1/README.md`, and `contest_cases.md` for strict teams, settled Flex Appeal, and the implemented core.

## In flight
- Flask/UI boundary is now implemented for the narrow V1 flow; no marketplace, roster valuation, scraping, or deployment work was added.
- Current public GameBlazers rules remain a future revalidation concern despite the settled private V1 configuration.

## Next
- Revalidate current public GameBlazers contest rules before expanding beyond the private V1 flow; run locally with `cd lineup_optimizer && .venv/bin/python app.py`.
- Keep multiple lineups, locks/exclusions, saved sessions, scoring, and marketplace features out of V1 core work.

## Blockers
- No public GameBlazers API, SDK, marketplace route, or documented current export was found.
- No stable athlete/Item ID exists in audited CSV schemas; source-row IDs remain diagnostic only.
- Do not pursue certificate-pinning bypasses, hidden-endpoint bypasses, scraping, bots, automated marketplace actions, or unauthorized copying.
