# Ink fidelity under lossy compression

Experiment date: October 5, 2026 (America/Denver). The hypothesis of a universal q2 operating recommendation was rejected. A reproducible, material ink-prediction failure was established; therefore this remains a useful diagnostic contribution rather than being presented as a successful compression recommendation.

## Main result

All 128 frozen test records completed: 12 non-overlapping scored windows, six physical segment IDs, three scrolls, two released model seeds. Each window has raw/Zstd/q2/q8 arms; eight fine-pitch windows also have q2/q8 before-depth-pooling arms. Candidate quality q2 was selected only from development w035. The frozen threshold was 0.5.

| Model-input setting | Median actual store savings vs native Zstd | Mean paired AP change, segment grouped | 95% group bootstrap interval | Worst window/seed AP change | Verdict |
|---|---:|---:|---|---:|---|
| q2 | 4.56x | +0.00805 | [-0.00870,+0.03235] | -0.04678 | Operating gate failed |
| q8 | 15.74x | -0.02393 | [-0.06452,+0.01749] | -0.18777 | Material adverse cases; no global effect claim |

The positive q2 mean is not an established improvement: its one-sided lower95 bound is -0.00607, below the preregistered -0.005 budget. Its worst F1 loss is 0.04937, exceeding 0.01. Actual q2 stores are 3.76-9.90x smaller, with padding/metadata included, but storage reduction alone does not meet the task-fidelity gate.

Three example failures:

| Region | Seed | Setting | Raw AP | Compressed AP | AP change |
|---|---:|---|---:|---:|---:|
| PHerc0841, auto-grown20260220144552896, window0 | 42 | q8 | 0.68264 | 0.49487 | -0.18777 |
| PHercParis4,20230702185753, window0 | 43 | q8 | 0.97316 | 0.82625 | -0.14691 |
| PHerc0841, same auto-grown segment, window1 | 43 | q2 | 0.61986 | 0.57308 | -0.04678 |

The last case has mean SSIM 0.9512 across the 17 planes actually supplied to the model. This does not establish a universal SSIM threshold; it shows why a visual-quality metric cannot substitute for an ink error budget.

q8 losses larger than 0.03 occur on four segments across PHercParis4 and PHerc0841. Those scrolls are physically distinct. No claim that every named segment is statistically independent of every other segment within its scroll is necessary for the strongest cross-scroll failure examples. The grouped intervals have only six segment groups and are descriptive; within-scroll correlation and three total scrolls limit generalization.

## Compression placement

| Scroll | Mean AP change: q8 on pooled model input | Mean AP change: q8 before depth pooling |
|---|---:|---:|
| PHercParis4 | -0.04773 | -0.00542 |
| PHerc0841 | -0.01754 | +0.01267 |

These are paired placement measurements on the same underlying regions. The direction and magnitude vary by window and seed; the better group mean is not a new safe operating recommendation. Compression before-depth-pooling operates on the published XY-level2 surface array, not original full-resolution CT. Native9 inputs use no pooling.

The bounded **original native9 CT -> TIFXYZ -> render -> model** experiment also completed: two development subwindows, two seeds, raw/Zstd/q2/q8. Raw-render correlation against published renders exceeds0.999998 on those crops; lossless decoded CT gives the same rendered input. Largest q8 AP loss there is 0.00740, much smaller than some model-input cases. This distinction is important: the study does not certify or condemn the full compressed CT mirror from its pooled-input results.

## Controls and reproduction

- Repeated raw pilot inference: max absolute float difference 0.
- Raw versus lossless predictions throughout the frozen test: max difference 0.
- Matched models, depth, orientation, patch origins, stride 64, Hann blending, FP32 and TF32-off in every pair.
- Restricted `weights_only=True` checkpoint loading; exact checkpoint hashes and complete state-key matching.
- First render probe initially failed because an even 28-plane stack was centered incorrectly. C++ source inspection established half-voxel centering and nearest vertex normals. Corrected correlation 0.999965; byte-truncated MAE 0.00330. The failure and correction are retained in the log.
- Separate empty-cache reproduction of the two strongest failures on different scrolls acquired 42 source objects, approximately 54.6 MiB, checked against original hashes. All 24 associated model-arm probability files, decoded arrays and metrics matched exactly. This is reproduction of selected failures, not new held-out validation.
- Maximum allocated GPU memory in the full test was 351,271,936 bytes (about 335 MiB). Maximum observed end-arm RSS was 1,747,447,808 bytes (about 1.63 GiB). The additional precision-controlled reproduction records an OS peak working set of 2,092,941,312 bytes (about 1.95 GiB) and verifies FP32 convolution output directly. This reproduction is a bounded subset, not a claim about peak RAM for every possible input.
- Package tests: 22 passed. Pinned upstream inference tests: 19 passed. Pinned upstream numerical/geometry tests: 14 passed. Deprecation warnings originate in Torch/SimpleITK, with no failing tests. Timing fields are available, but some initial jobs overlapped; no inference-speedup claim is made from those timings.

## Labels and exposure

Supervision masks define scored background. Unlabelled pixels are not silently counted as negatives. AP is step-integrated average precision, as implemented by scikit-learn, rather than a trapezoidal approximation. AP and F1 are label-agreement measures, not letter legibility or independently established physical ink truth. The source includes hand/pseudo-labels; no IR-fragment claim is made.

PHerc0139 native w040/w044 occur in the released model's embedded training configuration. Paris4 was a training scroll, and exact alias mapping for these historical surfaces has not been independently certified. PHerc0841 is outside the documented training-scroll set. Baselines on some PHerc0841 windows are weak, including below the prevalence baseline; compression-related gains there cannot establish recovered letters. “Frozen test” means untouched by this project's development, not necessarily by the released models.

## Useful action

Preserve original/lossless inputs for evidence-sensitive work until task-specific, representation-specific validation passes. Do not use a codec quality value, file-size ratio or positive average score as a substitute for adverse-case checks. This package provides the paired measurements and explicit rejection verdict needed to make that decision reproducible.

The contribution differs from the codec author's prior CT-image and surface-teacher checks: it measures masked ink labels through actual surface/preprocessing/inference workflows, includes both seeds and placement arms, enforces an operating budget, retains a rejected candidate, and supplies a repeatable cross-scroll failure example. It does not claim ownership of the codec, models, ordinary validation techniques or existing model-sensitivity warning.

No new First Letters finding exists. The current evidence is useful for protecting future searches from input-induced false negatives, not for asserting ten recovered letters.

Artifacts: [scores](scores.csv), [all numerical records](benchmark-records.json), [summary and gates](summary.json), [model-input image quality](model-input-quality.json), [source receipts](source-receipts.json), [frozen protocol](../experiments/TEST_PROTOCOL.md), [log](../research/LOG.md).
