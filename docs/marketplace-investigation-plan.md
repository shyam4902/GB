---
title: GameBlazers Marketplace Investigation Plan
status: planned
scope: NFL marketplace data access only
created: 2026-08-12
---

# GameBlazers Marketplace Investigation Plan

## Goal

Determine whether the current official GameBlazers client exposes a usable, authorized way to retrieve marketplace data for the user's own analysis, without contacting GameBlazers unless all technical alternatives are exhausted.

This is a discovery effort only. Do not modernize projections, contest rules, lineup optimization, or the web UI until marketplace access is understood.

## Current Findings

- The checked-in repository has no current GameBlazers API client. It only consumes exported CSVs and a historical SQLite database.
- The public site `https://www.gameblazers.com/` is live and exposes Football, Golf, Blog, Help, Terms, Privacy, and Contact links.
- `https://www.gameblazers.com/marketplace` returned HTTP 404.
- `https://www.gameblazers.com/api` returned HTTP 404.
- The public homepage exposed Next.js resources, AppsFlyer links, and analytics assets, but no public marketplace API host, developer documentation, or export feature was visible.
- The official Help Center still contains a Marketplace category and documents marketplace behavior.
- Official mobile clients are available for iOS and Android. The immediate investigation target is the user's iPhone/iPad client.
- The repository's SQLite copy contains historical `sales_history` data through May 12, 2025. It is historical context, not a current marketplace feed.

## Next Session: Authorized Client-Traffic Test

1. Use the official iPhone/iPad app normally and only with the user's own account/session.
2. Connect the device to the Mac and, if practical, use a local HTTPS debugging proxy with a normally trusted certificate.
3. Capture only a short marketplace read session: open marketplace, search/filter, inspect an item, and view the user's own relevant history if needed.
4. Do not submit purchases, listings, account changes, or automated actions.
5. Redact cookies, authorization tokens, device identifiers, payment data, account identifiers, and personal information before analysis.
6. Identify the read-only request host, endpoint shape, request parameters, response schema, pagination, timestamps, and stable item/listing identifiers.
7. Test whether an observed read response can be replayed for the user's own session without automating the app or bypassing authentication.
8. If the app refuses normal proxy inspection, stop. Do not bypass certificate pinning, modify the app, decompile protected binaries, or defeat access controls.

## Fallback Order

1. Normal authorized client-traffic observation, if technically available and permitted.
2. App-supported download, share, copy, or account-data export discovered through ordinary UI use.
3. Local importer for a user-provided CSV/JSON/report.
4. Existing SQLite database as historical-only reference.
5. Contact GameBlazers for an export/API request only as a last resort.

## Boundaries

- No code changes, database relocation, or dependency installation is part of this plan yet.
- Do not pursue hidden endpoints, authentication bypasses, certificate-pinning bypasses, scraping, bots, or automated marketplace actions.
- Do not send an external support request without the user's explicit approval.
- Keep the investigation limited to NFL marketplace data; other project workflows are deferred.

## Potential Deliverable After Discovery

If an authorized response format is available, add a small marketplace adapter that:

- stores raw snapshots separately from normalized records;
- validates prices, timestamps, expiration, listing state, and duplicate IDs;
- records ingestion time and source metadata;
- keeps current marketplace observations separate from historical sales;
- accepts an externally located database path through configuration rather than copying the database into the repository.
