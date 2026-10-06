# Spec: Report evidence integrity

Status: within Patrick's approved continued CPU-only validation work. New evaluator checks receive a separate draft PR for human review.

## Requirements & Goals

- Reproduce whether the released report accepts an incomplete experiment matrix when total rows and unique run IDs still equal128.
- Reproduce whether inconsistent stored AP deltas can hide the actual q8 failure while underlying metrics stay unchanged.
- If confirmed, reject malformed/mixed evidence before writing report artifacts. Preserve all original scores, source/model pins and statistical rules.
- Audit all published128 real-data records against the stronger contract and determine whether published conclusions require correction.

## Inputs, Outputs & Behavior

- Inputs: released frozen manifest and numerical records; deliberately damaged private copies only. No GPU, new data, labels or inference.
- Baseline: the v0.2.0 reporting command. Case1 replaces one lossless arm with a duplicate q8 cell under a different run ID. Case2 changes q8 delta fields while preserving recorded AP metrics. Save baseline behavior and exact mutation descriptions.
- Derive expected window/seed/arm/placement identities from the manifest; require each exactly once, correct physical/sample identities and matching manifest/source/model/inference contract.
- Check paired AP/F1 deltas against raw anchors, consistent denominators/thresholds, F1 confusion-count arithmetic and actual storage ratio arithmetic. Require finite values and byte-exact lossless input. Retain the producer's1e-6 lossless prediction tolerance; a claimed zero difference must also have identical prediction hashes/metrics.
- Do not reconstruct missing measurements, choose a different baseline or change uncertainty/gate formulas. Invalid evidence yields an actionable error and no newly written report.
- Outputs: regression tests, stronger validation, numerical audit receipt, research log and a reviewable draft PR. Published reference records remain immutable.

## Edge Cases & Error Handling

- Missing/duplicate/unknown cells, wrong seeds/placements/groups, inconsistent metrics/ratios, undefined/nonfinite scores, bad manifest hashes and broken lossless controls must fail.
- Valid public records must pass without numerical changes. Allow a declared1e-12 absolute tolerance for stored floating arithmetic; do not require new runtime identity fields absent from the original release.
- Report validation is consistency checking, not authentication of arbitrary user-supplied data or proof of physical ink truth.

## Acceptance Criteria

- [x] Both hypotheses tested through the actual released report command, with preserved damaged-input receipts.
- [x] A confirmed flaw is fixed at the evidence boundary before report writes, not hidden in plotting or warnings.
- [x] Every published record passes the stronger contract and the regenerated numerical summary remains unchanged, or a correction is explicitly documented.
- [x] Meaningful regressions cover matrix identity, paired arithmetic, denominators/thresholds, ratios and lossless controls.
- [x] Tests/lint/CI and valid/invalid end-to-end CPU commands pass; original data/results unchanged.
- [x] Research log and scientific-review draft PR prepared; no unauthorized merge/outbound message or prize/First Letters claim.
