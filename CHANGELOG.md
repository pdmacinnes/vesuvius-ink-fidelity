# Changelog

## Unreleased copied-label repair

- Verify copied label metadata/shards against their acquired source and atomically restore mismatched or partial targets instead of trusting existence.
- Matching copies are reused; interrupted repair preserves the prior target and permits retry. Actual Vesuvius-data replay restores identical decoded labels.
- Acquisition/evaluator changes await review; no source labels, model scores or v0.2.0 assets changed.

## 0.2.0 - October 6, 2026

- Exploratory boundary-padding and source-reference normalization diagnostics, reusing the official model and decoder with unchanged baseline settings.
- Both padding candidates fail the prewritten adverse-case rule; no new compression policy is promoted. AP and fixed-threshold F1 disagree severely in one counterfactual.
- Numerical receipts, negative results, tests and public-install reproduction evidence; reviewed in PR #3. Diagnostic padding remains experimental and is not a recommended storage policy.

## 0.1.1

- The short `reproduce` command uses published reference records and source receipts, so a new checkout can reproduce reported failures without first running the full benchmark.
- Explicit local result/receipt overrides remain available.
- Added default-input regression tests and documented the shortest public reproduction path.
- Scientific parameters, frozen ROIs, existing reference scores and conclusions are unchanged.

## 0.1.0 - October 6, 2026

- Initial reviewed release: paired real-data ink compression benchmarks, native Windows setup, raw CT/TIFXYZ rendering, depth-pooling comparisons, rejection gates and numerical evidence.
