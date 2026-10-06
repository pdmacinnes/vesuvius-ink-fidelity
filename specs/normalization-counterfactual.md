# Spec: Compression and normalization counterfactual

Status: part of Patrick's pre-approved next-stage research/GPU window. New experimental evaluator code is retained for human scientific review before promotion.

## Requirements & Goals

- Follow the rejected padding-policy hypothesis with a bounded diagnostic: does recomputing the existing robust patch normalization on decoded input account for some ink-score changes?
- Reuse the pinned official normalization/model/inference. No training, new labels, checkpoint selection or modification of published scores.
- Use the same two post-test development regions and both seeds. These cases remain exploratory and are not fresh validation.
- Compare raw; ordinary zero-q8; q8 normalized using raw-reference clipping/affine calibration; a fully frozen raw-input control.
- The reference-calibrated arm requires original input and is a causal counterfactual, not a deployable method or general safe-compression claim.

## Inputs, Outputs & Behavior

- Inputs: original model-input arrays, their q8 reconstructions, fixed supervision and released models.
- Reuse the upstream FlatBlockDataset through a wrapper, retaining block indices and metadata. Generate normalization from the public official raw-normalization function, then express the decoded-minus-raw clipped perturbation in that raw transform's units.
- Recover the effective affine scale from the official raw normalized input/output; do not silently substitute a new fallback normalization. Constant clipped raw inputs require an explicit constant-case rule.
- Verify a frozen-raw control is prediction-file identical to published raw. Preserve coordinate/depth/precision/weight/mask/threshold invariants.
- Report AP/F1/probability changes, calibration parameters/distribution and any failure. Compare both seeds/cases without choosing a policy from test scores.

## Edge Cases & Error Handling

- Reject mismatched patches and unsupported preprocessing; retain finite float32 output.
- Do not confuse empty raw support with normalization failure. Record/freeze raw occupancy for the counterfactual so decoder-created empty-region signal cannot silently alter tile scheduling.
- Reconstruct the reference normalization from its actual public output. If an affine calibration is undefined or a raw-control mismatch occurs, decline the experiment rather than claim a result.
- State the approximate effective-scale recovery and test it against the official transform; no copied or modified upstream implementation.
- Stop new GPU work by18:08UTC unless extended.

## Acceptance Criteria

- [x] Raw-reference normalization/control matches the official raw path within the declared numerical tolerance and prediction hash.
- [x] The decoded arm retains real data/shape and reports the unchanged source/mask/model contract.
- [x] Both seeds on both exploratory regions are scored; adverse/undefined cases are retained.
- [x] A mechanism conclusion is limited to these controlled cases; no production recommendation or new letters claim.
- [x] Tests, parameter receipts, research log and a scientific-review draft PR are prepared.


Acceptance note: the exact frozen-raw prediction control passes. The diagnostic produces a mixed negative result and is not promoted as a method.
