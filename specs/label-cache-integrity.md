# Spec: Copied label cache integrity

Status: within Patrick's continued CPU-only reliability work, pre-approved for implementation. Any new evaluator/acquisition changes receive a draft PR before release.

## Requirements & Goals

- Reproduce whether `mirror_label_array` returns a stale/corrupted copied shard merely because its target exists, despite acquiring a checksum-verified original object.
- Exercise both a valid but modified label shard and a truncated shard in an isolated copy of actual Vesuvius data. Never modify the main cache or reference labels.
- If confirmed, make verified source bytes authoritative and repair mismatched/missing targets atomically. Reuse the existing acquisition path rather than introduce a cache service or new format.

## Inputs, Outputs & Behavior

- Inputs: one original public label array from the frozen manifest, source receipts and separately copied encoded cache objects.
- Baseline: current released mirror helper. Compare decoded hashes before mutation, after a valid local label edit and after truncation followed by refresh/restart.
- Outputs: atomic label metadata/shard copy, source-hash verification on refresh, regression tests, real-data before/after receipt, research log and draft PR.
- A healthy matching target is reused. A mismatched target is replaced from the verified cached source via a temporary file and atomic replacement. Interrupted repair never replaces the existing target with partial bytes.
- No new inference, labels, model/data interpretation or external message is part of this task. All original dataset/reference files remain immutable.

## Edge Cases & Error Handling

- Missing/corrupt source still fails through Fetcher receipts; repairing a target never bypasses source checks.
- Preserve valid targets on interrupted write, clean temporary files, and make a retry restore the exact source bytes.
- Reject a local array whose decoded label checksum remains different after refresh; do not relabel or change supervision thresholds to compensate.

## Acceptance Criteria

- [x] Both corruption hypotheses reproduced on an isolated actual label array, or precisely rejected.
- [x] Valid but changed and truncated copied shards recover source-exact bytes/decoded labels.
- [x] Interrupted replacement preserves the previous target and retry repairs correctly; healthy cache reuse verified.
- [x] Tests/lint/CI and real-data replay pass; all original cache/data/reference files unchanged.
- [x] Numerical audit, research log and a separate reviewable draft PR prepared; no unauthorized merge/outbound/GPU work.
