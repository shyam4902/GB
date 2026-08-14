# Optimizer V1 Exact-Duplicate Manifest

**Audit date:** 2026-08-13  
**Scope:** `GameBlazers/`, `GB2/`, `dfs_optimizer.html`, `lineup_optimizer/`, `data/`, and `Projections/`, excluding nested `.git` metadata and `.DS_Store` files.

## Decision

No files were deleted.

The hashes below confirm byte-for-byte duplicates, but the archive paths are retained because they preserve historical provenance (for example, a copied roster inside the dated working archive, a numbered prototype iteration, or a duplicate legal document under a separate filename). No duplicate path was referenced by source-code search as an application dependency. Retaining the paths is safer than collapsing historical evidence during this audit.

## Exact duplicate groups

| SHA-256 | Paths | Canonical/reference choice | Deletion result |
|---|---|---|---|
| `320527c95db2d2e59713b06d094c4f4dafe20c69610f54587b7cd4399e94b9f2` | `data/raw/My_roster.csv`; `GameBlazers/rosters/My_roster.csv` | `data/raw/My_roster.csv` is the project data-path copy; the `GameBlazers/` copy preserves archive provenance | Not deleted: archive copy retained |
| `2eeec11d7ed5f43b980692076ed1b8a3e070e25627c0e172984e2bc5647755b0` | `lineup_optimizer/uploads/active_roster_jaz_copy.csv`; `GameBlazers/rosters/active_roster_jaz copy.csv` | `lineup_optimizer/uploads/active_roster_jaz_copy.csv` is the app upload-path copy; archive copy preserves source context | Not deleted: archive copy retained |
| `c024040b48bc6dd3f231bb17dde6bc918f38eab7ad1045326a647bcb9550f15a` | `lineup_optimizer/uploads/active_roster_shyam_copy.csv`; `GameBlazers/rosters/active_roster_shyam copy.csv` | `lineup_optimizer/uploads/active_roster_shyam_copy.csv` is the app upload-path copy; archive copy preserves source context | Not deleted: archive copy retained |
| `485510f1b061c8cd40f126cd7c37a15f817855911dfadc6dd0d7db251c84146d` | `Projections/GameBlazers.Rmd`; `GB2/GameBlazers.Rmd`; `GB2/GameBlazers (1).Rmd` | `Projections/GameBlazers.Rmd` is the documented pipeline path; both GB2 copies preserve archive provenance | Not deleted: archive copies retained |
| `331c4f36953dd8fbbb334053c56b609c6cc1da286f4ebecfb0c3217d7e8922e7` | `lineup_optimizer/app.py`; `GB2/app (2).py` | `lineup_optimizer/app.py` is the `Procfile` deployment target; GB2 copy preserves archive provenance | Not deleted: archive copy retained |
| `1c957382cf030a2c97c8cfc6533db9129aeeb4548722a492a7f08705084e6527` | `GameBlazers/lineup optimizer/lineup_builder (1).html`; `GameBlazers/lineup optimizer/lineup_builder (2).html` | Keep both numbered archive paths because the folder is a historical prototype archive | Not deleted: provenance retained |
| `568ec8b3bdfb6d42b0c4dfc433d326c17467794376587a0826f099809bc37c51` | `GameBlazers/lineup optimizer/lineup_optimizer_standalone (3).html`; `(4).html` | Keep both numbered archive paths because filenames encode the copied iteration | Not deleted: provenance retained |
| `7a41e6ddd37d12bb0ccef01f5d04416472a5e1ff0f16c464d23351fec9cf73d4` | `GameBlazers/lineup optimizer/lineup_optimizer_standalone (5).html`; `(6).html`; `(7).html`; `(8).html`; `(9).html` | No single canonical archive filename can be selected without discarding iteration provenance | Not deleted: provenance retained |
| `1081b7da55dbeae203e9b4c3c986625dd181ce9d841ba76f94ae7477603465fc` | `GameBlazers/terms.pdf`; `GameBlazers/terms_GB.pdf` | Keep `terms.pdf` as the natural document name; preserve the alternate copy because both are historical legal artifacts | Not deleted: legal/archive provenance retained |

## `.DS_Store`

`.DS_Store` files were excluded from the hash audit and were not removed. They are not part of the optimizer evidence packet, but deleting them was outside the exact-duplicate deletion decision made here and is deferred.

## Reference checks

- `lineup_optimizer/Procfile:1` selects `lineup_optimizer/app.py` as the deployment entry point.
- `Projections/GameBlazers.Rmd` is the documented projection pipeline path.
- The duplicated roster uploads are historical input artifacts, not required imports from application source.
- No source file reference was found that requires any duplicate archive pathname.

The absence of deletion is intentional: the user authorized exact-duplicate deletion, but also required preservation of historically meaningful version folders and evidence. The latter condition applies to these archive copies.
