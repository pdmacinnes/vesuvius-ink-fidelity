# Spec: Thin-stack boundary padding experiment

Status: included in Patrick's October 6 next-stage spec pre-approval and 90-minute GPU authorization. Experimental code/results receive a draft PR for scientific review before being recommended as a new production method.

## Requirements & Goals

- Diagnose whether the unused part of a volcomp boundary chunk contributes to the large ink errors observed after depth pooling.
- volcomp uses independent16³ DCT blocks in128³ chunks. A21-plane model input has only5 real planes in its second DCT block; zero padding introduces an artificial boundary. The model's centered17-plane input includes three planes from that boundary block. This mechanism is a hypothesis, not a result.
- Compare zero padding with edge/reflect continuation only to the next16-plane block boundary; retain zero fill beyond it to avoid encoding107 synthetic planes unnecessarily.
- Preserve the original shape, real voxel values before compression, weights, orientation, normalization, stride, precision, masks, metrics and thresholds. No new codec format or learned model.
- Use raw/zero-q8/tail-restored/tail-only-damaged controls to distinguish boundary-block effects from quantization of interior blocks.
- Existing scored regions are exploratory/development evidence. If a candidate helps, evaluate at most one fixed policy on separately frozen, previously unscored regions; do not call reused regions held out.
- Retain original v0.1 reference artifacts and report any negative result. No universal safe lossy setting or new letters are inferred from a mean score gain.

## Inputs, Outputs & Behavior

- Inputs: existing real public model-input Zarrs and aligned supervised regions; fixed seed42/43 checkpoints; pinned volcomp1.3.0; published original records and source receipts.
- Outputs: plane-wise codec error, unchanged-full-block checks, per-seed masked AP/F1, probability drift, actual stream/store sizes and an exploratory or confirmation verdict.
- First run edge/reflect and causal replacement controls on the worst cross-scroll cases. Confirm that full16-plane blocks decode identically when only padding changes.
- Select at most one extension policy from development evidence using mean AP improvement versus zero padding across both seeds, with adverse cases reported. Freeze a fresh-region manifest before new inference.
- Confirmation target: at least three additional physical segments, two windows each, both seeds, raw/zero-q8/fixed-policy-q8, and exact lossless controls. Regions already scored in v0.1 or development are excluded.
- Any encoded experimental Zarr retains the real declared shape and unchanged decoder/codec identifier. Record padding policy in attributes. Zarr recommends fill values beyond array bounds; this exploratory encoder continuation is an explicit deviation from that recommendation, while only in-bounds decoded values are used by the model. Test standard-reader compatibility and do not promote a writer without review.

## Edge Cases & Error Handling

- Reject wrong dtype, dimensions above128, unsupported policy or empty dimensions. Leave full-size chunks unchanged.
- Preserve exact real input voxels before encoding; q=0/Zstd must restore in-bounds voxels exactly for every policy.
- Do not change unused values by allocating an arbitrarily larger physical array or shifting chunk origins. Bound continuation to the codec block boundary.
- If full interior blocks change, investigate codec/global behavior rather than assuming boundary isolation.
- A policy that harms a seed/region, increases bytes excessively or fails confirmation remains a negative result.
- Fresh-region data/label/frame and source-hash checks follow the existing evaluator. Undefined labels/metrics do not produce convenient zero scores.
- Stop new GPU jobs by approximately18:08UTC (12:08pm America/Denver) unless Patrick extends authorization.

## Acceptance Criteria

- [x] Prior-art check identifies the exact remaining question and credits the existing codec and boundary convention.
- [x] All padding policies preserve real voxels before encoding and pass exact lossless controls.
- [x] Interior-block isolation and plane-error patterns are measured on actual Vesuvius inputs.
- [x] Both model seeds and causal replacement controls are evaluated on clearly labeled exploratory regions.
- [x] Any selected candidate is fixed before scoring fresh confirmation regions; confirmation/adverse results are all reported.
- [x] Stream/storage overhead and standard Zarr reader compatibility are verified, with the fill-value recommendation deviation stated.
- [x] Original published reference scores/manifests are unchanged; tests and scientific-review draft PR are prepared.
- [x] No external adoption, safe universal recommendation, First Letters discovery or prize outcome is asserted.


Acceptance note: both extension candidates failed selection. Fresh confirmation is correctly not applicable; it was not run. The completed exploratory diagnostics are a draft review candidate, not a promoted writer.
