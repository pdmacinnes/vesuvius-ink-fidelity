# October 2026 Progress Prize draft

Status: stable evaluator reviewed, merged and publicly released as [v0.3.0](https://github.com/pdmacinnes/vesuvius-ink-fidelity/releases/tag/v0.3.0) on October6,2026. Community use and actual submission remain pending. This document does not submit anything. The official October31,11:59pm Pacific deadline was rechecked October6 at [the prize page](https://scrollprize.org/prizes#progress-prizes).

## Contribution

Vesuvius Ink Fidelity: a task-aware, reproducible evaluation of lossy CT/surface-input compression through actual ink-model workflows. It imports the existing volcomp codec and released ink_9um models rather than introducing a new codec or model.

## Problem and usefulness

The compressor already has CT-image, surface-teacher and probability-store measurements and warns about model sensitivity. What remained unmeasured in the inspected release was masked ink-label sensitivity across native/pooled representations, both model seeds and compression placement, with an explicit operating-budget decision. This project makes that question reproducible and supplies concrete adverse examples instead of a general warning.

## Evidence

- 12 frozen scored windows, six physical segment IDs, PHerc0139/PHercParis4/PHerc0841; two fixed released seeds; 128 completed paired records.
- Raw/repeat and lossless controls match exactly. A real original-CT -> TIFXYZ -> render -> model path passes published-render parity and was evaluated on two development subwindows.
- q8 model-input compression loses as much as 0.18777 masked ink average precision and produces material failures on four segments across two scrolls.
- q2 produces 3.76-9.90x smaller actual stores but fails the preregistered task budget. Its positive overall mean is explicitly not used to certify the setting.
- A separate empty-cache reproduction of the two strongest failures on different scrolls matches all 24 decoded input, prediction-file and score records exactly, with source hashes enforced.
- A genuinely fresh public Windows checkout/environment/compiler/models also reproduces all24 records exactly using the documented short command. A missing-public-input default was fixed in v0.3.0 without changing scores or scientific parameters.
- Before-versus-after depth pooling measurements demonstrate that the stage of compression matters. Those arms are clearly separated from the native9 raw-CT experiment and do not certify the full compressed mirror.

## Integration and reproducibility

Standard original Zarrv2 CT/surface arrays, standard Zarrv3 label shards, TIFXYZ geometry and ordinary Zarr/TIFF/JSON/CSV outputs. CLI commands cover pilot, frozen benchmark, raw-CT experiment, report, image quality and reproduction. Sources, model hashes, ROIs, masks, parameters, scores and adverse cases are documented. Windows-native setup and native codec DLL are tested on an RTX5070Ti; peak allocated GPU memory for the test is about335MiB.

## Originality and limits

The codec, models, generic validation methods and prior model-sensitivity findings are upstream work and are credited. This project adds an ink-specific end-to-end evidence package, placement comparisons, rejection rules, source-verified reproduction and a reusable evaluator. It does not claim new letters, a new best model, universal compression safety, or independently verified physical ink truth.

Some evaluated surfaces appear in the released model's training set. The masks include human/pseudo-labels; PHerc0841 raw baselines can be weak. Results concern paired input sensitivity and label agreement. Confidence intervals use six physical segment groups and remain broad; there is no global significant-improvement claim.

## Open-source and adoption status

New code is MIT. Fetch manifests and numerical records are release-ready; original CT, labels, meshes, weights and candidate textual images are excluded. No new textual revelation is published. No external adoption or organizer endorsement has been established, and no community messages have been sent.

Before submitting: obtain genuine usage/feedback where possible, verify the current October form/rules, and link the final public release and reproduction commands. A modest Progress Prize is the realistic target; the evidence does not justify a $20,000 expectation.

Reviewed follow-up: [40 exploratory mechanism records](../reports/MECHANISMS.md) reject both simple boundary-continuation repairs and show that raw-reference normalization barely repairs the two largest failures. One intervention improves AP while fixed-threshold F1 collapses. These commands/results were reviewed and merged in PR #3; they are not required to reproduce the original submission evidence and do not imply a safe compression policy.
