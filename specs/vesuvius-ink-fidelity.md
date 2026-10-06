# Spec: Vesuvius Ink Fidelity

Status: approved by Patrick in chat, October 5, 2026: "i confirm you may begin". Research date: October 5, 2026.

## Requirements & Goals

- Build an open-source, native-Windows-first Python package/CLI that measures how CT compression affects the real Vesuvius ink pipeline and produces actionable, reproducible evidence. The PC has an RTX 5070 Ti with approximately 16 GB VRAM; no paid/cloud compute is planned.
- Use actual public Vesuvius CT, paired TIFXYZ surfaces, released models and ink/supervision labels. Compare against pinned official inference on raw and byte-exact lossless inputs. Synthetic fixtures support tests but cannot constitute the contribution's scientific evidence.
- Investigate a specific unresolved gap: ink-label sensitivity through **compression -> surface rendering -> pooling/normalization -> inference**, separately from existing image-quality, surface-teacher and probability-store compression measurements.
- Reuse SuperOptimizer/volume-compressor; do not create a new codec or claim its compression ratios as our work. Pin its source and cite existing downstream studies. Refresh its code, issues and related Villa PRs before starting each experiment.
- Quantitatively demonstrate either (a) a useful storage/transfer improvement within an explicit ink-fidelity budget, or (b) a new, meaningful ink failure mode and a practical mitigation. A runnable benchmark without new actionable evidence is not a successful research outcome.
- Maintain `research/LOG.md`, a source/provenance manifest, preregistrations, complete experiment tables and negative results. Distinguish observed facts, other authors' claims and our hypotheses.
- Ship a simple CLI, tests, install instructions, benchmark manifest, reproducible report and examples suitable for modular integration. Maintain `FEATURE_MAP.md` as features become implemented.
- Code license: MIT with upstream notices. Data/weights remain under their own terms. Source URLs and hashes are published; raw CT, labels, meshes and weights are not bundled by default. Potential new textual discoveries remain private.
- Scope excludes frontier model research, large-scale training, a new workflow control plane, a whole-scroll codec mirror, an OCR/text generator and a generic checkpoint leaderboard. No First Letters or prize-winning claim follows from prediction agreement alone.

### Hypotheses and prior-art boundary

H1: high CT PSNR/SSIM can coexist with a material loss or spurious gain of ink evidence, with sensitivity depending on the position of compression relative to rendering/pooling.

H2: an operating point selected on development ROIs can preserve ink recovery on separate test ROIs while reducing bytes/time relative to raw/lossless storage or mitigating the released lossy default.

H3: existing decode smoothing that improves CT appearance does not necessarily improve ink detection. Test only a documented upstream smoothing setting rather than inventing a large search.

Already solved or measured: a volume codec and compressed mirror; surface-teacher disagreement; probability-threshold-preserving compression; generic ink checkpoint/validation/depth studies; simple provenance checks. Our result must explicitly differ from these. See `research/ECOSYSTEM_AND_OPPORTUNITIES.md` for sources and ranked alternatives.

### Baselines and immutable controls

1. Raw input through the pinned official model and preprocessing, with fixed tile origin, stride, blend, depth convention, precision and masks.
2. Lossless Blosc/Zstd input, exact decoded voxel equality, same downstream computation.
3. Existing volcomp quality settings q=2/4/8 with plain decoding. q=0 is an optional codec parity check, not a replacement for the Zstd comparator.
4. One documented upstream smoothing arm at an appropriate lossy setting.
5. The published mirror's matching level/quality only after exact source identity and preprocessing provenance are verified. Otherwise use local encode/decode of the same pinned original chunks and label that comparison accurately.

Use fixed seed42/seed43 final ink_9um checkpoints. Do not choose a different checkpoint independently for each compression arm. The canonical 2 µm model is a confirmation arm only if it fits and the first experiment merits expansion.

### Model and implementation tiers

Selection/spec/statistical interpretation: most capable tier. Ordinary Python package, format readers, CLI and test implementation: balanced tier. Source refresh, manifest formatting and routine report checks: fast tier. No agent swarm is needed. Actual model availability/settings must be respected; these are routing preferences, not evidence that a runtime model has been switched.

## Inputs, Outputs & Behavior

### Inputs

- Local or public HTTPS Zarr v2/v3 arrays and OME-Zarr groups. Resolve axis order, pyramid level, dtype, physical units and coordinate transforms explicitly.
- TIFXYZ directories with `x.tif`, `y.tif`, `z.tif`, `meta.json`, optional mask; preserve documented validity and grid-density semantics. An explicit frame override is accepted only when recorded in the run manifest.
- Surface-volume Zarr and aligned ink/supervision TIFF or Zarr masks. Unlabelled pixels are unknown unless an explicit trusted negative mask says otherwise.
- Pinned official model checkpoint and embedded/configured preprocessing; input domain, normalization and depth direction are recorded. Prefer safe checkpoint loading supported by the pinned model; never execute arbitrary unverified serialized input.
- A JSON experiment manifest with exact sample/scan/volume/segment/model IDs, source URLs, hashes where available, chunk keys, ROI origin/shape, physical scale, supervision source, model training-exposure status, split role and compression arms.

### First data targets

- Pilot: PHerc0139 native 9.362 µm volume `20250728140407`, segment `20260317000000-w035_2026031718`, its matching native surface and mesh. Reachability and raw chunk sizes have been checked; label acquisition and render parity still need verification.
- Pipeline-order arm: matching PHerc0139 2.399 µm source `20260102150214` and render, pooled by the exact official recipe for ink_9um.
- Expanded controls: labeled PHercParis4/PHerc1667 representations and PHerc0841. Select exact assets before preregistration. Any IR-fragment control is additional and must have verified alignment.
- Final target: at least 12 non-overlapping scored windows from at least 6 physical segments and 3 scrolls, including an out-of-training-scroll stratum when the released model's provenance permits that conclusion. Prefer 4 scrolls. Do not treat native and pooled representations of one region as independent examples.

The preflight sample chunks are local/private and are not the final benchmark or a train/test set.

### Outputs

- Machine-readable per-run/per-ROI JSON and summary CSV: acquisition bytes, codec stream bytes, full stored bytes including padding/metadata/index, encode/decode/render/inference time, peak RAM/VRAM, input and prediction differences, label metrics, errors and controls.
- An ordinary Zarr/OME-Zarr derived input where needed, preserving physical origin and scale; prediction TIFFs and numerical arrays in separate artifacts. TIFXYZ is accepted unchanged for the render experiment and remains traceable in output metadata.
- Static exportable plots of bytes versus ink degradation, paired segment deltas, sensitivity by pipeline location and worst-case failures. Plots distinguish development/test data and unknown training exposure.
- A human-readable benchmark report with baselines, commands, machine details, uncertainty, limitations and a recommendation or explicit rejection/inconclusive verdict.
- A small example fetch/benchmark manifest, native PowerShell walkthrough and Python API documentation. External inputs are fetched from original public sources, not vendored into Git.
- A separate First Letters assessment entry after each experiment; any candidate images/data are excluded from public output by default.

### Normal workflow

1. After approval, initialize the local repository and feature branch. Keep research source snapshots/private data excluded from the eventual code release unless licensing/relevance supports inclusion. Reuse existing dependencies where possible.
2. Verify Python/PyTorch GPU support and native compiler/codec availability. Run a positive-control inference and a lossless codec round trip. If a native codec DLL build is impractical, test a minimal Windows-hosted WSL codec subprocess; record its boundaries and timing. Do not move inference to an unverified alternate environment.
3. Refresh relevant prior art. Acquire only bounded required chunks with atomic temporary writes, a byte budget and hashes. Reuse an established reader/cache rather than building a general downloader service.
4. Resolve one exact frame and create paired arms from the **same** source chunks. Raw-volume compression uses original globally aligned 128³ chunk/block coordinates; do not silently reanchor DCT blocks at each ROI crop.
5. Reproduce published surface-volume rendering on a small control region. Match normal direction, voxel/grid scale, interpolation, crop/UV origin and layer spacing. Set a documented intensity error tolerance from the raw reference before inspecting compression effects. If render parity fails, diagnose it; do not attribute the mismatch to compression.
6. Run the two-window pilot with fixed inference settings. Preserve identical valid area and halo. Measure raw repeatability. Verify raw and decoded-lossless input equality and prediction parity.
7. Compare compression placements as distinct factors: original CT before rendering; native rendered surface volume; and correctly pooled model input. Only test placements actually supported by the data/model. Padding of thin surface stacks must be excluded from quality metrics and included in storage accounting.
8. Use pilot/development ROIs to select at most one operating recommendation and fixed decision rules. Freeze an unseen ROI manifest and parameters **before** obtaining its ink scores. Source/shape checks may precede freezing; no model-output ranking may select test windows.
9. Evaluate the frozen test set with both model seeds and the selected arms. Include raw and lossless arms in every representation. Reuse raw predictions only when the full inference/input hash matches.
10. Compute paired results and grouped uncertainty. Generate full tables, failing controls, worst-case regions and limitations; keep unsuccessful arms in the research log.
11. Release code/documentation early if the result passes its research gate. Invite use through a prepared draft; sending Discord/email/other messages requires Patrick's explicit instruction. Prepare a public PR with human review and auto-merge off. Resolve the GitHub destination from the user's account/project context before publication.
12. Refresh October rules and prior art, assemble a submission-ready report, and evaluate First Letters prospects. Submission is a separate final external action; this spec does not fabricate community usage or papyrological validation.

### Measurement contract

- Primary scientific quantity: paired change in **masked ink PR-AUC**, with ROC-AUC secondary, plus Dice/F1 at a threshold chosen only on development data. Report both seeds and each segment, not only a pooled pixel score.
- Supervision masks define valid negatives. A mask drawn only on positive strokes cannot support full PR-AUC; such data can support explicitly limited retention/prediction measures, or be omitted from that metric.
- Primary fidelity quantity where trustworthy labels are unavailable: raw-versus-compressed probability drift and precision/recall of raw predictions at a fixed decision threshold. Call this prediction agreement, not ground-truth accuracy or legibility.
- Measure faint-stroke and confident-background strata defined from development labels/raw predictions, fixed before test scoring. Report absolute and relative losses; never hide a weak raw baseline behind a relative improvement.
- Measure PSNR/SSIM, MAE, spatial error tails and air-mask changes as explanatory metrics. They do not substitute for ink outcomes.
- Use float predictions where the pinned official implementation exposes them; otherwise retain the official quantized output and handle ties correctly. Record truncation/rounding. Display-adjusted maps cannot be scored.
- Statistical unit is the physical segment/region group. Use paired group bootstrap with fixed seed and report sample counts. No pixel-iid confidence intervals. With too few groups or broad intervals, explicitly return inconclusive.
- Timing: cold/warm acquisition separately; encode/decode CPU time separate from rendering/GPU inference. Report median of three short timing repetitions where useful; do not rerun expensive model arms just to manufacture precision. Local byte savings are not a measured network speedup.
- Repeated inference/numerical noise is measured before a fidelity threshold is interpreted. Reject claimed improvements comparable to that noise.

### Preregistered research gate

The pilot may refine practical bounds, but the final test gate must be frozen before test scoring. Default targets:

- **Useful operating improvement:** at least 2x fewer fully accounted bytes than lossless Zstd on the same nonempty corpus, with one-sided grouped 95% lower confidence bound for PR-AUC change no worse than -0.005, no observed physical segment worse than -0.02, and absolute Dice/F1 drop no more than 0.01 at the frozen threshold. Report raw baseline quality and abstain for labels/strata that cannot support the claim. A different error budget must be justified in development and explicitly preregistered.
- **Meaningful failure with mitigation:** at least 0.03 absolute masked PR-AUC loss on two independent physical segments, or a preregistered substantial confident-background/false-negative change, independently reproduced; demonstrate that raw/lossless or a selected codec setting avoids the effect. Quantify incremental value relative to the upstream already-known surface-teacher disagreement. If it is only a trivial known warning, the gate fails.
- Treat detected disagreement without label support as a failure of reproducibility/fidelity only, not a recovery accuracy failure. It needs a concrete pipeline consequence to meet the project objective.

These are decision criteria, not results or assurances that compression is universally safe.

### Pivot policy and schedule

- Spend no more than two focused days on initial build/acquisition/parity. Resolve concrete blockers directly; if feasibility fails, log the failure and select another evidence-backed project.
- Reject the ink direction if prior art already covers the exact end-to-end result, controls fail, or effects are negligible and no useful operating improvement emerges. Do not turn an empty benchmark into a prize story.
- First bounded pivot: the same codec/CT infrastructure, but test **thin-sheet/instance identity consequences** against actual labeled surface blocks and raw m7 baseline. Confirm label defects first and keep teacher agreement distinct from truth. Write a spec amendment before materially different implementation, per Patrick's standing rule.
- Target early useful code October 13-17; final reproduction/review by October 28; submission materials by October 30. Approval timing and actual measured runtime may change these dates; log changes rather than compress validation to fit the deadline.

## Edge Cases & Error Handling

- Zarr groups, plain arrays, v2/v3 metadata and different separators: resolve explicitly, test supported paths and give a nonzero actionable error for unsupported codecs/schema. Do not silently read an empty/missing pyramid as valid zeros.
- Empty/padded chunks, crop boundaries and thin surface stacks: preserve fill values, score only original valid voxels, account for storage overhead, and keep interpolation/model halos sufficient. No empty-air domination of reported compression ratios.
- Missing physical units, conflicting volume IDs, invalid mesh sentinels, nonfinite coordinates or wrong handedness: fail with required metadata/override details before computing a scored render. Never infer physical scale from TIFXYZ grid density alone.
- Mesh normals inverted or depth window off-center: reproduce a known positive control and fixed render parity first; keep orientation identical across compression arms. A failure here is a harness fault, not an ink-compression result.
- Mismatched labels/UV canvas: require exact shape/transform provenance and visualize permitted known-text alignment; no silent resize/shift or label-driven best alignment on the test set.
- Positive-only labels, empty supervision, one-class windows or no usable ink: report undefined metric and reason; never return a convenient zero/one. Preserve exclusion counts and denominators.
- GPU OOM: lower batch size only, keeping ROI, tile size, stride, normalization and precision fixed. Record the retry. If the model still cannot fit, drop a secondary arm explicitly rather than change it invisibly.
- Unsupported RTX/PyTorch runtime or codec platform: resolve dependency/build compatibility in the environment phase, with a documented WSL codec fallback if verified. No unsupported inference substitutions.
- FP16/nonfinite outputs: first run full precision where supported; fail on nonfinite values instead of replacing them with zero. Mixed precision requires a separate parity control and is not selected independently by compression arm.
- Network interruption or checksum mismatch: retry bounded transient errors through the existing reader where possible; reject deterministic/corrupt data. Final outputs are atomic and marked complete only after valid metrics/provenance are written. A failed arm remains failed in the report.
- Data/model revision: do not mix changed bytes under an existing result key. Hash mismatch invalidates the cached result and is recorded. Resume only matching completed arms.
- Codec instability or lossy zero-mask ringing: measure and expose it; no preprocessing that quietly repairs only compressed inputs. A documented common mask can be applied to all arms and evaluated separately.
- Compression before versus after pooling changes the experiment: label each arm clearly. Keep representation family and real physical scale, including anisotropic depth sampling, in provenance.
- Claimed First Letters patterns appearing only in compressed input: treat as suspect until raw CT and independent controls support them. Never synthesize or complete letterforms, publish a new discovery, or claim a prize from a row score.
- Licensing uncertainty: retain input manifests and numerical evidence; exclude data/weights/new textual images from public release until the applicable terms are resolved. Do not alter upstream originals.

## Acceptance Criteria

- [ ] A refreshed prior-art audit shows a specific remaining ink-compression gap and credits the existing codec, surface-model measurements and ink tooling.
- [ ] Native Windows installation and a real positive-control ink inference run succeed on the RTX 5070 Ti; any codec WSL dependency is explicit and verified.
- [ ] At least one complete real CT -> TIFXYZ render -> preprocessing -> official model -> scored output path is demonstrated; a surface-volume-only experiment is labeled as such.
- [ ] Raw rendering parity is established on a small published reference region with fixed coordinate/depth conventions before compression comparisons.
- [ ] Raw vs lossless decoded voxels match exactly and repeated/pair inference satisfies the documented numerical tolerance.
- [ ] At least 12 frozen test windows, at least 6 physical segments, and at least 3 scrolls are scored with paired baselines and both fixed ink_9um seeds; training exposure and non-independent representations are identified.
- [ ] Supervision/negative masks are respected; no unlabelled pixels are silently treated as trusted background, and undefined metrics carry explicit reasons.
- [ ] Compression quality and pipeline placement are separated; original chunk origins, padding, halos, physical units, codec bytes and storage overhead are correctly recorded.
- [ ] A quantitative operating improvement or new material failure with an actionable mitigation passes the preregistered gate on real data; otherwise the original idea is rejected/pivoted.
- [ ] Results include per-segment and seed deltas, grouped confidence intervals, full denominators, adverse cases, runtime and peak memory. Prediction agreement is never mislabeled as legibility/ground truth.
- [ ] Tests cover format/frame/mask behavior, lossless round trip, fixed-metric known answers/ties, empty/one-class handling, numerical failures and interruption/resume integrity. Existing relevant upstream checks run and pass.
- [ ] One clean-cache bounded real-data reproduction completes with recorded input/output hashes and commands; numerical differences meet the declared tolerance.
- [ ] README/API/PowerShell instructions, data/model provenance, license/notices, benchmark examples, feature map, preregistration and research log are complete and accurate.
- [ ] Public release artifacts exclude unapproved raw data/labels/weights and potential new textual discoveries; a human-reviewed branch/PR has auto-merge off.
- [ ] First Letters assessment is updated after each substantive experiment, with eligibility, exposure, raw-evidence support and reasons to proceed/stop. No qualifying discovery is claimed without organizer review.
- [ ] A submission-ready evidence report is prepared, with conservative prize framing and fresh deadline/rule checks. No completion, adoption or prize claim is made before the corresponding evidence exists.
