# GameBlazers Optimizer V1 Readiness Audit Plan

> **For agentic workers:** This is an evidence-audit plan. No production optimizer implementation is part of this plan.

**Goal:** Convert the historical GameBlazers optimizer, roster, projection, and contest archive into an implementation-ready V1 evidence packet without changing production behavior.

**Architecture:** Preserve the existing Flask deployment boundary as the likely future implementation target, use the golf browser optimizer only as an exact-search reference, and use the later football browser prototypes for domain/UI behavior. Record all conclusions as confirmed, historical, inferred, or unresolved, with direct paths and line/function evidence.

**Tech Stack:** Python standard library/pandas for read-only analysis scripts, existing HTML/JavaScript/Python/R/CSV/XLSX/PDF artifacts, Markdown documentation, and minimal CSV fixtures. No new dependencies or production code.

---

### Task 1: Establish the evidence inventory

- [ ] Read the required project documents completely.
- [ ] Inventory every optimizer, roster, projection, contest, and discovery artifact.
- [ ] Compute SHA-256 duplicate groups inside and outside historical folders.
- [ ] Record line numbers/function names for meaningful optimizer behaviors.

### Task 2: Measure schemas and identity behavior

- [ ] Parse every roster CSV/TXT and projection CSV/XLSX sheet.
- [ ] Build a schema matrix covering headers, types, statuses, positions, teams, names, multipliers, projections, and ID availability.
- [ ] Count repeated athlete names, exact duplicate rows, and same-athlete variant rows.
- [ ] Run progressive exact/normalized name matching across all usable roster/week combinations.
- [ ] Record unmatched, ambiguous, team-conflict, and explicit-alias candidates.

### Task 3: Reconcile contest and optimizer lineage

- [ ] Compare active Flask, alternate Flask, golf exact search, standalone football, and meaningful browser-builder families.
- [ ] Extract contest configs from code and screenshots.
- [ ] Verify Flamethrower from archived sources and preserve the Wildfire/Volcano naming conflict.
- [ ] Document the historical 50% minimum-spend rule as configurable evidence, not a universal rule.

### Task 4: Prepare fixtures and cleanup decision

- [ ] Create minimal provenance-labeled fixture rows covering valid shapes, Flex/Superflex, duplicates, matching, ineligible projections/statuses, multiplier-once, infeasibility, greedy counterexample, and no-partial-lineup behavior.
- [ ] Check references and provenance for exact duplicates.
- [ ] Delete only duplicates that meet every authorization condition; otherwise document why they remain.

### Task 5: Publish and verify the readiness packet

- [ ] Create/update `docs/optimizer-v1-readiness.md` with contract, lineage, schemas, measured matching, duplicate-card policy, contest matrix, solver requirements, reusable/rejected code, fixtures, unresolved decisions, and implementation sequence.
- [ ] Update `STATE.md` only with material audit state.
- [ ] Verify line references, counts, fixture provenance, duplicate cleanup status, and no production-code changes.
- [ ] Report the smallest next implementation task.
