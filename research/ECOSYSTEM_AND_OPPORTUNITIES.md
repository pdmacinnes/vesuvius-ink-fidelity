# Vesuvius Challenge: October 2026 contribution selection

Research date: October 5, 2026, America/Denver. Status: researched proposal, not an implemented or prize-ready result.

## Recommendation

Build **Vesuvius Ink Fidelity**: an independent, reproducible benchmark of how lossy CT compression changes ink recovery through the actual rendering, resampling, normalization and inference pipeline. Produce measured operating recommendations and a small reusable evaluator, using the existing compressor rather than developing a competing codec.

The distinguishing question is: **which compression settings and pipeline locations preserve usable ink evidence, and where does an apparently good image-quality score conceal a material loss or spurious gain in ink predictions?**

This currently has better expected community value within the deadline than another checkpoint sweep, generic reproducibility framework, surface metadata auditor, or cross-scan alignment report. The recommendation remains conditional on a two-day novelty/feasibility experiment. A general warning that models dislike compression is already known and is insufficient as our contribution.

## Scope and evidence quality

Reviewed the live prize rules, official open problems and wishlist, data formats and curated datasets, model cards, current Villa source, public community project catalog, recent awards, and linked reproductions. An anonymous GitHub API snapshot contains **107 open issues and 79 open PRs**. This is a snapshot, not a count of confirmed bugs. Detailed source inspection focused on ink inference, normalization, patch discovery, geometry, metrics, and the proposed compressor and registration extensions.

Villa source pin: `0e14cf48c8cee74b11e5e40a9d1d520b74e35423`.
Volume-compressor pin: `20b03983ee741baa160d3e630da77a3b3a24ee44`.
Released ink_9um model repository pin: `7109667e2607db1b90c37c8b09cb876ea7fe7bb1`.

Public issue comments provide useful community signals, including maintainer corrections and review. Private Discord history was not accessible or inspected; no authenticated Discord/community connector was used. Public Discord links and prize announcements are pointers, not evidence of private community endorsement. No one has been contacted, no tool has been adopted on our behalf, and no prize submission has been made.

Search coverage is substantial but not exhaustive. Search engines missed several recent repositories that were discoverable from GitHub comments. Refresh open PRs, issue comments and relevant repositories before implementing each hypothesis, and again before release.

## Prize and release constraints

The live [prize page](https://scrollprize.org/prizes#progress-prizes) states an October 31, 2026, **11:59pm Pacific** deadline. The best monthly submission receives $20,000; other awards vary by contribution. Early release, actual use, real-data evidence, useful diagnostics and documentation matter. Awards are discretionary, not a metric leaderboard.

The [First Letters rules](https://scrollprize.org/prizes#first-letters-prizes) require 10 legible letters within one 4 cm² region of an eligible volume, reproducible surface/image evidence and safeguards against invented text and training overlap. Technical and papyrological review are necessary. A new textual discovery must remain private until the organizers authorize its announcement.

The [recent winner list](https://scrollprize.org/winners) already recognizes the July validation harness, windcheck, TIFXYZ Doctor, catalog auditing and consumer-GPU spiral fitting. August includes checkpoint benchmarking, depth-slice experiments, a First Letters workflow report and checkpoint repairs. Large awards went to substantive unwrapping systems. A benchmark is realistically a $500-$2,500 contribution unless it produces a widely used, substantial pipeline improvement; $20,000 is a stretch, not our forecast.

## Hardware fit

Observed locally: RTX 5070 Ti, **16,303 MiB VRAM**, NVIDIA driver 581.57; approximately **426 GiB free** on C:. The initial folder is empty and not a Git repository. Python, RAM, native compiler availability, supported PyTorch CUDA build and WSL availability remain unverified. Do not interpret an unavailable PATH command as proof that a tool is absent.

Prefer a Python CLI with bounded ROI downloads, batch-one inference, no training by default and cached raw predictions. The existing native codec uses C23 and was measured under WSL2; native Windows codec integration must be demonstrated, not assumed. A Windows-hosted WSL codec subprocess is an acceptable fallback if needed, with inference and analysis on the Windows GPU. No paid compute is required or planned.

## Ecosystem map and avoided duplication

| Component | Role and current integration | Implication |
|---|---|---|
| [Villa](https://github.com/ScrollPrize/villa), especially `vesuvius/` | Current Python data, model and inference tooling | Reuse pinned inference and preprocessing; avoid old standalone package examples where they disagree with main. |
| [VC3D](https://github.com/ScrollPrize/villa/tree/main/volume-cartographer) | Interactive tracing, inspection and rendering | TIFXYZ/OME-Zarr compatibility is the adoption path. A Python-only result should export ordinary artifacts and exact render settings. |
| [Lasagna](https://github.com/ScrollPrize/villa/tree/main/lasagna) | Joint surface/fiber optimization | Surface snapping is existing work, not a novel project by itself. |
| [Spiral fitting](https://github.com/ScrollPrize/villa/tree/main/spiral-fitting) | Global winding solution | Windows and consumer-GPU fixes, input checks and reproducibility work are crowded. |
| [ScrollFiesta](https://github.com/Hob3rMallow/scrollfiesta_public) and patch connectivity work | Automatic meshing/unwrapping | Strong previous awards; rebuilding them would be inappropriate. |
| [Ink validation harness](https://github.com/khj1222/vesuvius-challenge) | Whole-region splits, CV, depth attribution, adaptation, label budgets and recent fiber agreement experiments | Much broader than its July award description. Generic validation, pseudo-label evaluation and label-free threshold experiments overlap heavily. |
| [labelscope](https://github.com/rodriguescarson/labelscope) | Leakage checks, split repair, label diagnostics and CT sheet-switch detection | Generic blocked CV or a dark-seam detector already exists. |
| [vesuvius-repro](https://github.com/TAUIL-Abd-Elilah/vesuvius-repro) | Regional m7 reproduction and further failure analysis | A regional prediction reproduction alone is not new. |
| [vesuvius-ladder](https://github.com/nerln/vesuvius-ladder), [inkfloor](https://github.com/nerln/inkfloor) | Duplicate surfaces and prediction disagreement from input derivations | Duplicate discovery and intensity-floor measurements already have asset-pinned reproductions. |
| [TIFXYZ overlap audit](https://github.com/koreanjys/tifxyz-overlap-audit) | Detects multiply owned normal-band voxels | Remaining gap is downstream ink attribution/benefit, not demonstrating overlap again. |
| [ARGUS](https://github.com/Cinder-Covenant/ARGUS) | Provenance, identity checks, research resources and controls | Avoid creating a general workflow control plane or another identity wrapper. |
| [First Letters survey](https://github.com/Bullo27/first-letters-survey) | End-to-end native-resolution ink search and negative-result calibration | Simply running the workflow on unread scrolls is already covered. |
| [volume-compressor](https://github.com/SuperOptimizer/volume-compressor) | Released CT codec, compressed mirror, Zarr codec and pending VC3D support | Reuse it. Its existing downstream surface-teacher and probability-storage tests must be credited and distinguished from our ink-specific end-to-end study. |

Other pending Villa PRs further reduce easy novelty: inference sweep [#1872](https://github.com/ScrollPrize/villa/pull/1872), trained-form checks [#1897](https://github.com/ScrollPrize/villa/pull/1897), blank-output probes [#1924](https://github.com/ScrollPrize/villa/pull/1924), point/interface registration scoring [#1945](https://github.com/ScrollPrize/villa/pull/1945), frame provenance [#1944](https://github.com/ScrollPrize/villa/pull/1944), retries [#1919](https://github.com/ScrollPrize/villa/pull/1919), and multiple native-3D preparation speedups.

## Ranked concrete opportunities

These are subjective planning estimates, **not statistically measured prize odds**. Difficulty, originality and usefulness use a 1-5 scale, with 5 highest. Adoption probability means meaningful use by at least one external contributor/maintainer after a useful release. `P(done)` means a genuinely differentiated, demonstrated result by October 31, conditional on approximately 80-120 focused engineering hours and access to this PC. Each probability has at least ±15 percentage points uncertainty.

The ranking score is `usefulness × P(done) × P(adoption) × originality / 5`. It estimates community value, not dollars. Prize ranges are conditional on success and submission; a $0 outcome remains possible for every project. GPU hours are broad order-of-magnitude budgets on this PC, not measured 5070 Ti timings. CPU RAM figures are target peaks.

| Rank | Remaining problem and proposed contribution | Difficulty | Compute / local data | Originality | Usefulness | Adoption | Plausible award | P(done) | Value score |
|---:|---|---:|---|---:|---:|---:|---|---:|---:|
| 1 | **Ink task fidelity under CT compression:** measure before-render vs after-render vs after-pooling sensitivity; recommend tested settings under explicit error budgets | 3 | 6-20 GPU h; 4-16 GB RAM; 2-20 GB ROI data | 4 | 5 | 65% | $1,000-$2,500; $5k only with substantial adopted improvement | 75% | 1.95 |
| 2 | **Residual cross-scan deformation after affine refitting:** local correspondence correction with cycle-consistency and abstention, beyond the existing stronger affine | 4 | 4-15 GPU h; 8-16 GB RAM; 5-25 GB | 4 | 5 | 65% | $1,000-$2,500 | 45% | 1.17 |
| 3 | **Compression-aware thin-surface preservation:** test whether visual fidelity hides fused/lost sheet boundaries against actual instance labels, beyond teacher agreement | 4 | 10-30 GPU h; 8-16 GB RAM; 3-15 GB | 4 | 5 | 55% | $1,000-$2,500 | 50% | 1.10 |
| 4 | **Topological evaluation insensitive to real repairs:** add sheet-identity/merge consequences and validate against tracer behavior rather than merely reporting a metric blind spot | 4 | 5-20 GPU h; 8-16 GB RAM; 2-8 GB | 3 | 5 | 60% | $1,000-$2,500 | 45% | 0.81 |
| 5 | **Physical cross-representation train/test exposure:** 3D-aware exclusion across distinct segment names and scan representations, beyond 2D region splits and patch-bbox leakage | 3 | 4-15 GPU h if training comparison; 4-12 GB RAM; 1-10 GB | 3 | 4 | 60% | $500-$1,000 | 50% | 0.72 |
| 6 | **Reliable First Letters negatives:** calibrate the existing synthetic detectability probe against real low-contrast known ink and independent controls; distinguish unsupported negatives | 4 | 5-20 GPU h; 4-12 GB RAM; 2-10 GB | 3 | 5 | 55% | $1,000-$2,500 | 40% | 0.66 |
| 7 | **Hard-region annotation targeting that actually improves downstream topology:** prioritize compressed/curved failures and demonstrate fixed annotation-budget benefit against uncertainty sampling | 4 | 15-40 GPU h; 8-16 GB RAM; 3-10 GB; manual labeling | 3 | 4 | 55% | $1,000-$2,500 | 45% | 0.59 |
| 8 | **Transferable ink checkpoint selection:** test seed-stable, multi-domain ranking or calibrated abstention against the already-published failure of in-domain score ranking | 4 | 10-30 GPU h inference; 40+ if retraining; 2-15 GB | 3 | 5 | 55% | $1,000-$2,500 | 35% | 0.58 |
| 9 | **Remote long-run integrity after interrupted output:** real failure-injection/resume evidence preventing a partial TIFF from being treated as complete; extend pending retries without duplication | 2 | CPU plus 1-4 GPU h; 2-6 GB RAM; 0.5-3 GB | 1 | 4 | 80% | $250-$1,000 | 85% | 0.54 |
| 10 | **Normal-band ownership and wrong-sheet ink attribution:** quantify whether nearest-sheet ownership removes neighbor leakage without damaging actual strokes | 4 | 5-20 GPU h; 8-16 GB RAM; 1-8 GB | 3 | 4 | 50% | $1,000-$2,500 | 40% | 0.48 |
| 11 | **Loss/metric numerical contracts:** repair raw-logit Dice behavior and demonstrate an actual training consequence, rather than adding implementation-mirroring tests | 2 | 5-15 GPU h; 4-8 GB RAM; 0.5-3 GB | 1 | 4 | 80% | $250-$1,000 | 70% | 0.45 |
| 12 | **Localized pseudo-label error after geometric transfer:** confidently separate transferred-label misalignment from model disagreement; improve label transport beyond constant canvas shifts | 4 | 10-25 GPU h; 8-16 GB RAM; 3-15 GB | 3 | 4 | 50% | $1,000-$2,500 | 35% | 0.42 |

Ranks 1 and 3 overlap in infrastructure, but they are distinct scientific targets: ink evidence after a surface-conditioned pipeline versus preservation of sheet identity in raw volumetric segmentation. Pick one as the initial job. Rank 3 is a bounded pivot if ink provides no new material result.

### 1. Ink task fidelity under compression - selected

Evidence: [VC3D codec PR #1704](https://github.com/ScrollPrize/villa/pull/1704) and [compressor downstream tests](https://github.com/SuperOptimizer/volume-compressor/blob/main/docs/deblocking.md). The compressor already measures image quality, surface-teacher disagreement and probability-map compression; it explicitly warns that existing models are sensitive. This gap is **not** the absence of all downstream tests. The reviewed files do not provide paired human-label ink metrics through native and pooled renders, pipeline-order isolation, or ink-specific operating recommendations.

Baseline: raw/uncompressed and byte-exact Zstd input through pinned official inference, plus the released lossy settings. Intervention: evaluate compression location/quality and choose an operating point on development ROIs only. Required outcome: independently demonstrated ink failure with a practical avoided loss, or a tested storage/runtime improvement within a preregistered ink error budget on separate ROIs. Risk: no ink-specific effect beyond already-known surface sensitivity, weak labels, build friction, or upstream simultaneous work.

### 2. Residual local registration beyond affine

Evidence: [#1912 and its comments](https://github.com/ScrollPrize/villa/issues/1912), [texture-based transform check](https://github.com/TAUIL-Abd-Elilah/pherc0139-scan-transform-check). The latter already reports a strong held-out affine refit. A [CT-only depth selector](https://github.com/neg-0/vesuvius-research/tree/main/v013-pherc0139-depth) failed its registered held-out test. Do not repeat either experiment as a new contribution.

Remaining experiment: compare smooth local correction with the stronger affine, holding out spatial blocks/segments and requiring cycle consistency. Baselines also include Lasagna refinement, if it applies to this target. Success needs materially smaller independent correspondence error and useful render/label consequences with no sheet switches. Risk: residual error is mostly measurement noise, making local flexibility overfit. This is why its completion probability dropped during research.

### 3. Thin-surface preservation under compression

Evidence: [surface wishlist #191](https://github.com/ScrollPrize/villa/issues/191), [compressor limitations](https://github.com/SuperOptimizer/volume-compressor), and [existing geometry diagnostics](https://github.com/Jinhojeong/vesuvius-surface-geometry-diagnostic). Teachers agreeing does not establish preservation of correct sheet identity. Baseline is raw CT m7 inference at identical stride and threshold; compare actual annotated merge/split consequences after compression. Success requires an actionable compression failure or better-quality operating point. Risk: instance ground truth has fused contacts and must not be treated as unquestioned truth.

### 4. Topology metrics with operational consequences

Evidence: the geometry-diagnostic report already demonstrates metric insensitivity to some merge repairs. Build only if a new metric predicts tracer sheet switching or a blinded expert ranking better than official topology metrics and existing connected-component diagnostics. Use repaired real labels and synthetic controlled contacts on real CT; validate on untouched labeled blocks. Risk: cheap new metrics score annotation artifacts or duplicate an existing metric implementation.

### 5. Physical cross-representation exposure

Evidence: [duplicate surface #1547](https://github.com/ScrollPrize/villa/issues/1547), [representation families #1582](https://github.com/ScrollPrize/villa/issues/1582), the July harness, and labelscope. Remaining gap is a physical-space exclusion across differently named/represented surface inputs, if absent in current tools. Baseline is each tool's current split/exclusion, not an intentionally bad random split. Success requires a real cross-split overlap missed by that baseline and an honest rescoring or retraining consequence. Risk: all relevant pairs are already grouped or lack authoritative frames.

### 6. Calibration of negative evidence

Evidence: [blank-output probe PR #1924](https://github.com/ScrollPrize/villa/pull/1924), [held-out transfer failure #1867](https://github.com/ScrollPrize/villa/issues/1867), and first-letters-survey. Synthetic ink planting is already implemented; another probe would duplicate it. Test whether its detectability threshold predicts recovery of real, known ink under controlled degradation, comparing raw positive controls and simple input-quality diagnostics. Success is calibrated scope/abstention with demonstrated prevented false negatives. Risk: synthetic and real ink differ too strongly, leaving an interesting rejection but no better tool.

### 7. Annotation targeting with measured benefit

Evidence: [label-generation wishlist #193](https://github.com/ScrollPrize/villa/issues/193) and the official [open-problem discussion](https://scrollprize.org/2026_open_problems). Existing uncertainty/triage tools make another ranking report insufficient. Compare fixed numbers of newly refined hard-region labels selected by failure anatomy, uncertainty and random controls; retrain a small existing model and evaluate held-out topology. Risk: human label time and short training comparisons may exceed October's budget.

### 8. Checkpoint selection that transfers

Evidence: #1867 already tests all fourteen ink_9um checkpoints and shows the failure of in-domain ranking; other contributors have decomposed seed versus step variation. Remaining target is better selection/abstention that generalizes to an unseen domain. Baseline includes last checkpoint, seed average and published validation winner. Require leave-one-scroll-out evaluation with genuine independent controls and grouped uncertainty. Risk: too few independent domains and seeds to validate selection, rather than fit the benchmark.

### 9. Partial output and resume integrity

Evidence: [remote read failure #1666](https://github.com/ScrollPrize/villa/issues/1666), pending [retry #1919](https://github.com/ScrollPrize/villa/pull/1919) and [partial TIFF cleanup #1967](https://github.com/ScrollPrize/villa/pull/1967). The still-useful experiment is end-to-end failure injection, interruption and restart on real ROIs showing output equivalence to a clean run. Prefer extending those PRs over a new workflow layer. Novelty is low and likely award modest; adoption odds are relatively good if it reveals an uncovered failure.

### 10. Ownership-aware ink attribution

Evidence: [#1150](https://github.com/ScrollPrize/villa/issues/1150) already shows normal-band collisions and changed CT reducers. Compare current render sampling with ownership restriction, using known positive stroke regions and conservative neighbor controls. A multiply-owned voxel count is insufficient; show a real incorrect attribution avoided or retain an explicit inconclusive verdict. Risk: material nearer a neighboring mesh can still be correct context, and masking it changes the model's training distribution.

### 11. Loss numerical behavior

Evidence: [raw-logit Dice issue #1488](https://github.com/ScrollPrize/villa/issues/1488). The fix itself is known; establish whether the affected path is used in a current configuration and run a matched short training comparison before claiming impact. Baseline must be the exact faulty path, not another architecture. Risk: dead/unused path or upstream fix eliminates the project; fold into an upstream patch, not a prize centerpiece.

### 12. Pseudo-label transfer with local confidence

Evidence: [accurate 3D labels #192](https://github.com/ScrollPrize/villa/issues/192), [s2slabmap](https://github.com/OliverDaubney/s2slabmap), official tifxyz_label_transfer, and the new PHerc0139 transform/label analysis. Existing constant canvas corrections already explain substantial apparent misalignment. Remaining contribution would separate local residual geometric uncertainty from prediction differences and exclude uncertain labels instead of reinforcing them. Baseline includes corrected canvas shift and affine. Risk: correspondence and teacher errors are not independent, so a lower model loss need not mean truer labels.

## Data and model plan for the selected project

[Official curated datasets](https://scrollprize.org/data_datasets) distinguish current surface/ink labels from archived fiber and instance bundles. Scroll ink masks are hand annotations or pseudo-labels, not independent infrared ground truth. Use supervision masks wherever supplied, report provenance, and keep label agreement separate from verified readability.

Primary model: [ink_9um](https://huggingface.co/scrollprize/ink_9um), small hybrid 3D-to-2D models with two seeds. Published training includes PHerc0139, PHerc1667, PHercParis4 and PHerc0814. Use seed42/seed43 final checkpoints as fixed arms, not a new best-checkpoint search. A [canonical 2 µm model](https://huggingface.co/scrollprize/ink_canonical_2um) is a secondary confirmation arm if memory and runtime permit. Surface, winding, fiber/DINO and 1667-iteration models are relevant baselines for pivots, not an invitation to train them all.

| Data target | Purpose | Availability/status |
|---|---|---|
| PHerc0139, native 9.362 µm CT `20250728140407` | First raw-volume encode/decode -> TIFXYZ render -> ink_9um pilot | Raw metadata reachable; 128³ uint8 chunks, uncompressed. One actual 2 MiB nonempty CT chunk downloaded and hashed. |
| PHerc0139 w035 `20260317000000-w035_2026031718` | Paired native9 surface, mesh and labels | Surface metadata reachable: 28×5820×5240, chunks 28×128×128; one real 448 KiB surface chunk downloaded and hashed. Mesh metadata reachable. Native and 2.399 µm label paths are present in catalog. |
| PHerc0139 2.399 µm CT `20260102150214` and matching surface render | Isolate compression before vs after ~9.6 µm pooling | Catalog and exact source volume identified; raw ROI/label fetch still to be tested. |
| PHercParis4 and PHerc1667 labeled renders | Additional known-text domains and finer-pitch controls | Public dataset/tutorial/model sources inspected; specific ROI manifest pending. |
| PHerc0841 labeled segments | Unseen-scroll sensitivity stratum for ink_9um | Prior public reproduction shows reachable data and weak baseline transfer; fresh label/ROI acquisition still required. No claim that its low baseline proves absence of ink. |
| PHerc0500P2 photographed fragment | Independent-label control, if alignment/rights are clear | Conditional addition; do not delay the project for it or equate fragment morphology with rolled-scroll performance. |
| PHerc1203 or another currently eligible unread volume | Secondary First Letters raw-versus-compressed check | Only after control validation; cannot establish correctness without independent evidence. |

Exact preflight URLs, byte counts, hashes and observed intensity ranges are in `sources/input-preflight.json`. These are reachability checks, **not model benchmarks**.

## Original contribution and first experiment

The target deliverable is an ink-specific test suite and empirical operating table that downstream users can rerun on their own mesh/volume/model. Reuse existing codec and inference, preserve the same coordinates, depth, patch grid, normalization, precision, masks and thresholds across paired arms. Compressing the already rendered input is a separate arm, not a substitute for testing the raw CT mirror.

Start with two labeled PHerc0139 pilot windows and both fixed model seeds: raw/Zstd, volcomp q=2/4/8, with plain decoding and one upstream-recommended smoothing setting where applicable. Measure raw prediction repeatability first. Then ask whether changing compression placement before rendering versus after rendering/pooling changes ink sensitivity, and whether high PSNR/SSIM predicts that sensitivity.

Pilot results are development evidence. Fresh sealed ROI manifests and untouched regions are needed before claiming a recommended operating point. Reject a claim built on unmasked/unlabelled pixels, quantized display images, different patch strides, or different scans. Do not infer readability from a larger foreground area or from prediction agreement alone.

## Schedule and kill criteria

| Target date | Deliverable / decision |
|---|---|
| October 6-8, after spec approval | Working codec/inference pilot, positive control, raw-vs-lossless parity, updated novelty check. Stop if acquisition/build/inference cannot be made reliable within two focused days. |
| October 9-12 | Preregistered ROI manifest; development comparison; declare a useful signal or reject the ink hypothesis. |
| October 13-17 | Untouched ROI evaluation, paired uncertainty, reproducible figures, early public code candidate if meaningful. |
| October 18-23 | Documentation, native Windows reproduction, external usage invitation drafted; bounded pivot if needed. |
| October 24-28 | Final independent rerun and review; public PR/release and community feedback if authorized and repository destination resolved. |
| October 29-31 | Refresh rules/competing work, assemble evidence and submission draft. Aim to finish before deadline day. |

Pivot if the ink result only repeats the already-known teacher disagreement, gives negligible effects with no storage/use improvement, fails controls, or is already solved upstream. The first pivot is rank 3, ground-truth sheet-identity consequences of compression, with a short preregistered study using the same acquired CT and codec. Rank 2 is a later option only if there is independent evidence beyond the existing affine. A materially different implementation will receive a revised spec for confirmation under the standing approval rule.

## First Letters assessment

No First Letters discovery has been made. This project's direct chance of yielding a qualifying discovery by October 31 is low, estimated **below 5%**, and is not included in the Progress Prize value score. Its value is preventing a degraded input from producing a misleading negative and preserving confidence in later search.

After each real experiment, record: positive-control recovery, input-domain compatibility, whether raw CT supports any compressed-only patterns, physical surface identity, training exposure and candidate eligibility. Continue toward First Letters only if an eligible volume has stable, data-supported strokes across raw input and independent settings; retain private artifacts for organizer/papyrological review. Changing display contrast, model consensus, synthetic probe response or a high row score is not evidence of ten letters.

## Release and evidence hygiene

MIT for new code; keep upstream notices for reused code. Treat each input's own license and terms separately. The [catalog](https://vesuvius-challenge-open-data.s3.us-east-1.amazonaws.com/metadata.json) lists CC BY-NC 4.0 for selected assets, while the [data-server terms](https://dl.ash2txt.org/LICENSE.txt) additionally restrict redistribution and textual revelations. Publish fetch manifests, numerical tables and permitted plots; do not vendor raw CT, labels, meshes or weights by default. Resolve any inconsistent terms before redistributing data-derived images. Keep potential new text private.

Maintain a hypothesis/experiment log, hashes, commands, parameters, durations, peak memory, failures and revisions. Link all prior baselines. No software implementation, ML benchmark, adoption claim, commit or PR has been completed in this research phase. Implementation follows the companion spec after explicit approval.
