# GameBlazers Completed-Sales Backfill Handoff

## Objective

Continue building the local completed-sales database by retrieving older NFL sold listings at a deliberately very low request rate. This is a long-running background job; speed does not matter. Reliability, resumability, and avoiding unnecessary load matter most.

Do not work on active listings, valuation, roster analysis, or the lineup optimizer in this task.

## Current state

- Workspace: `/Users/shyampatel/Desktop/GB`
- Collector: `market_py/update.py`
- Tests/reference implementation: `market_py/test_update.py`
- Local database: `market_py/gameblazers.db`
- Existing database tables:
  - `sales_history`: 16,016 legacy rows
  - `marketplace_sales_v2`: 200 recent normalized rows
- `marketplace_sales_v2.listing_id` is the primary key and makes inserts idempotent.
- The collector reads `GB_ACCESS_TOKEN` from the environment and must never write or print it.
- `python3 market_py/update.py --self-test` currently passes.
- Local databases and backups are intentionally Git-ignored because the GitHub repository is public.

## Git status

- Main project branch: `codex/project-checkpoint`
- Main project PR: https://github.com/shyam4902/GB/pull/1
- Optimizer branch: `codex/optimizer-v1`
- Optimizer PR: https://github.com/shyam4902/lineup_optimizer/pull/1

Work only in the main `GB` repository for this task. Do not modify the optimizer repository.

## Required implementation

Modify the existing collector rather than creating a second scraping stack.

### 1. Add resumable historical backfill

The current `update_sales()` always begins at page 1 and stops when it reaches an existing listing. Preserve that behavior for recent incremental updates.

Add a separate backfill mode to the same script with:

- an explicit starting page;
- exactly one fetched page per scheduled run by default;
- a durable checkpoint recording the next page to fetch;
- the checkpoint stored locally beside the database and excluded from Git;
- idempotent inserts using the existing `listing_id` primary key;
- a command to inspect current checkpoint/status without making a request;
- a command to reset or set the checkpoint manually.

Do not infer progress from row count. Persist the exact next page only after the current page is successfully parsed and committed.

### 2. Conservative request behavior

Use these defaults:

- one page per invocation;
- one scheduled invocation every 60 minutes;
- no concurrent requests;
- no proxy rotation or account rotation;
- no automatic token extraction;
- no endless retries;
- keep the existing request/response schema unless current evidence proves it changed.

Failure behavior:

- `401`: stop and report that a fresh login token is required;
- `403`: stop without advancing the checkpoint;
- `429`: honor `Retry-After` when present, stop the current run, and do not advance the checkpoint;
- `5xx` or network failure: leave the checkpoint unchanged and let the next scheduled run retry;
- unexpected response structure: save no rows, leave the checkpoint unchanged, and report the page and response type without logging credentials or full private headers.

### 3. Database protection

Before the first backfill run:

- create a timestamped SQLite backup in `market_py/backups/`;
- verify the backup opens successfully;
- enable SQLite integrity checking before and after the first real run;
- commit each fetched page in one transaction;
- never delete or rewrite legacy `sales_history` rows;
- never replace the database with a test database.

### 4. Local scheduling

Set up a macOS `launchd` user agent, not a system-wide daemon.

Requirements:

- run once per hour;
- execute one backfill page and exit;
- use absolute paths;
- write concise stdout/stderr logs under `market_py/logs/`;
- do not place the access token directly in the plist, repository, command history, or log;
- if a durable token source is unavailable, install the job disabled and document the exact manual start command instead of inventing token-refresh automation.

Also provide commands to:

- load/start the job;
- stop/unload the job;
- inspect the most recent log;
- inspect the current checkpoint;
- run one page manually;
- restore the database backup.

## Tests

Add focused tests covering:

1. successful page commit advances the checkpoint once;
2. duplicate listings do not create duplicate rows;
3. `401`, `403`, `429`, network failure, malformed JSON, and unexpected response shape do not advance the checkpoint;
4. a rerun of the same page is safe;
5. status/checkpoint commands perform no network request;
6. one invocation fetches no more than the configured page limit;
7. logs never contain the access token.

Use fake HTTP responses for tests. Do not use the live endpoint in automated tests.

## Verification and first live run

After tests pass:

1. Report the proposed file changes and commands.
2. Back up and integrity-check the database.
3. With `GB_ACCESS_TOKEN` supplied only through the current shell environment, run exactly one backfill page manually.
4. Report:
   - requested page;
   - rows returned;
   - new rows inserted;
   - duplicates skipped;
   - next checkpoint;
   - total `marketplace_sales_v2` rows;
   - database integrity result.
5. Only install/enable the hourly job after that one-page verification succeeds.

## Scope limits

- Completed NFL sales only.
- No active listings.
- No purchasing, listing, account mutation, or browser automation.
- No changes to roster valuation or optimizer code.
- Never commit database files, backups, logs, checkpoints, tokens, cookies, or personal account data.

## Completion criteria

The task is complete when:

- backfill progress is resumable and inspectable;
- each run fetches one page and exits;
- failures never corrupt data or skip a page;
- the first manual page succeeds and the database remains valid;
- the hourly job can be started and stopped with documented commands;
- tests and the existing self-test pass;
- code and documentation are committed to a new `codex/` branch and pushed to the existing `shyam4902/GB` repository as a draft PR.
