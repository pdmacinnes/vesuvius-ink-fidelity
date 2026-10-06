# Review handoff - October 6, 2026

Reviewed version: [v0.3.0](https://github.com/pdmacinnes/vesuvius-ink-fidelity/releases/tag/v0.3.0), incorporating all three approved PRs. Historical v0.2.0 remains immutable. All original numerical evidence remains valid. The authorized [upstream request](https://github.com/SuperOptimizer/volume-compressor/issues/1) is posted; independent reproduction/adoption remains unestablished. No additional outward message or GPU work occurred during the latest CPU audits.

## Reviewed changes

| PR | Purpose | Evidence |
|---|---|---|
| [#6](https://github.com/pdmacinnes/vesuvius-ink-fidelity/pull/6) | Fix report completeness and arithmetic validation | Released reporter accepts a missing cell hidden by a duplicate and accepts deltas that hide four real failures. Fix rejects both. All128 real records validate; regenerated summary is byte-identical.52 local tests and Windows/Linux CI pass. |
| [#7](https://github.com/pdmacinnes/vesuvius-ink-fidelity/pull/7) | Repair copied label cache integrity | Actual PHerc0139 copied labels remain modified or truncated under old refresh. Atomic source-checked repair restores the exact decoded hash.39 local tests and Windows/Linux CI pass. |
| [#5](https://github.com/pdmacinnes/vesuvius-ink-fidelity/pull/5) | Add actual mirror integration probe | All98 native9 chunks and both historical rendered inputs match the local q8 baseline. Separate-cache CPU proof;46 local tests and Windows/Linux CI pass. Bounded compatibility, not general fidelity or fresh model performance. |

Patrick reviewed all three PRs; #6, #7 and #5 are now manually merged. Documentation overlaps were reconciled, preserving every audit and negative result. Auto-merge remains OFF.

## Combined verification

The three code/test patches applied cleanly together in an isolated local scratch checkout. All69 distinct tests pass, including native codec integration; lint passes. Regenerated original report summary is byte-identical. [Combined receipt](../reports/pending-integration-verification.json) identifies the exact tested commits. The independent counts above overlap and must not be added together as137 distinct tests.

The first scratch run failed because its temporary-test parent did not exist; a second environment check hit Git ownership protections on junctioned upstream repositories. Created the missing parent and ran as the owning user without modifying global Git safety settings. These were test-environment failures, not product/data failures.

The combined merged tree passes all69 tests and lint, and its original report summary remains byte-identical. The v0.3.0 wheel passes isolated module/CLI/version checks; original v0.2.0 assets and benchmark data remain immutable.

## Research next step

Seek an independent reproduction and concrete workflow integration from the public request. Additional replies/posts require Patrick's authorization. The First Letters secondary path still needs a verified eligible surface and a distinct problem beyond existing centering/registration work; none of these CPU integrity results establishes a new discovery.
