# Vesuvius engineering research log

## 2026-10-05 - Orientation and prior-art search

Status: research and specification; implementation awaits explicit spec approval under Patrick's standing instructions.

- Workspace initially empty, not a Git repository. No existing application or uncommitted changes.
- GPU observed: NVIDIA RTX 5070 Ti, 16,303 MiB reported VRAM, driver 581.57. C: free space approximately 426 GiB. RAM and Python runtime not yet verified.
- Live official rules confirm October 31, 2026, 11:59pm Pacific Progress Prize deadline. Search-index copy still says September: use live primary sources.
- Retrieved public Villa main tree and open issue/PR snapshots. Exact commit is in `sources/villa-head.txt`. Source code reads are research, not implementation.
- GitHub CLI config inaccessible in sandbox; anonymous public HTTPS/API reads succeeded with reviewed network escalation. No external account connector used.
- Reviewed official wishlist, open problems, data formats, curated datasets, ink tutorial, model cards, winners, and community-project index.
- Prior-art exclusions: generic ink checkpoint sweeps, ordinary held-out validation, generic TIFXYZ doctor, catalog audit, window-depth sweep, naive sheet-switch detector, simple Windows support, and regional m7 reproduction already have substantial public implementations.
- Critical findings from other contributors, NOT independently reproduced here: #1912 reports transferred PHerc0139 meshes off the March scan's ink-bearing sheet and an imperfect label-free depth workaround; #1867 reports weak ink_9um transfer; #1547 reports a duplicated PHerc0139 surface; #1150 already prototypes normal-band overlap ownership.
- Newly read pending PRs include inference sweep (#1872), representation checks (#1897), blank-output diagnostics (#1924), registration scoring (#1945), and frame preflight (#1944). A generic tool in any of these areas would risk duplication.

### Hypotheses under consideration

H1: CT-only local correspondence across scans can correct residual normal displacement/tilt of transferred surfaces more reliably than maximizing model foreground. This is untested. It must beat both the published mesh and the existing ink-based depth selector, and must abstain when matching adjacent wraps is ambiguous.

H2: Normal-band ownership improves ink attribution in compressed regions. Deferred because the public overlap-audit already demonstrates geometric collisions, and proving real ink improvement requires stronger ownership ground truth.

H3: Physical-coordinate splitting detects cross-segment leakage missed by 2D masks. Deferred because labelscope and the July winner already cover substantial leakage analysis; a remaining gap must be demonstrated before building another harness.

### Experiments / negative results

No ML experiments or new quantitative claims yet. All quoted existing measurements must be attributed to their authors. Failed network/runtime probes are environmental checks, not scientific negative results.

### Next evidence needed

Read the #1912 reproduction, existing registration/refinement implementations, and pending #1945 before selecting H1. Verify exact assets, licenses, coordinate conventions and small-region downloadability. Write ranked opportunities and a falsifiable implementation spec; obtain approval before coding.

## 2026-10-05 - Corrections, competing work and project selection

- Read #1912 comments rather than relying on its title. Maintainer jrudolph states the March-2026 IDs are export dates for July-2025 ROI scans, not March acquisitions. The report now separates scan identity from export identity; the manifest spec requires both. This prevents the same mistaken assumption from entering experiments.
- Another contributor already reports a 40,822-tile texture match and a stronger held-out affine refit for PHerc0139 2.4-to-9.4 um. A fresh CT-only depth selection attempt in neg-0/vesuvius-research failed its own held-out rule. Its finer foreground-based grid improved the mean but harmed aligned controls. These are their measurements, not ours.
- Decision: demote H1/local alignment. Any later version must beat the stronger affine and existing refinement, use independent regions, and handle ambiguous neighboring sheets. A max-foreground depth sweep is excluded as prior art.
- Inspected volume-compressor source, September submission, image benchmarks, decode-smoothing tests, Python interface and VC3D PR #1704. It already measures downstream surface-teacher agreement and compressed probability fields. Initially considering the gap as 'no downstream tests' was too broad; narrowed it to ink-label consequences through rendering/pooling and explicit task operating points.
- Selected hypothesis H4: compression placement and quality affect ink recovery in ways that image-quality metrics and existing surface-teacher checks do not adequately describe. Untested. Must yield an actionable ink result beyond the existing general model-sensitivity warning.
- Ranked 12 concrete remaining problems in ECOSYSTEM_AND_OPPORTUNITIES.md. All difficulty/probability/award forecasts are subjective and conditional; none are empirical prize odds.
- Public input preflight succeeded: PHerc0139 native9 raw CT metadata, w035 surface metadata and matching mesh metadata; released ink_9um model files exist. Downloaded one raw 128^3 uint8 CT chunk (2,097,152 bytes) and one 28x128x128 surface chunk (458,752 bytes), both nonempty, with hashes in sources/input-preflight.json. No model run was performed.
- Environmental negative results: sandbox blocked ordinary network and GitHub CLI config reads; reviewed anonymous HTTPS worked. PowerShell returned metadata bodies as byte arrays for octet-stream; corrected the saved metadata to UTF-8 JSON and revalidated shapes. These are preflight issues, not scientific negatives.
- Licensing check: selected catalog assets list CC BY-NC 4.0; the data-server terms also restrict redistribution and new textual disclosures. Release design excludes raw assets/weights and candidate text by default and uses original-host manifests.
- Created specs/vesuvius-ink-fidelity.md with paired baselines, raw/lossless controls, held-out ROI rules, grouped uncertainty, explicit success/rejection criteria, standard format support, tests, Windows requirements and First Letters assessment.

### Current state / next action

Research selection and spec are ready for review. No implementation, ML benchmark, new model metric, test suite, Git commit, PR, community outreach or submission exists yet. Await Patrick's explicit confirmation of the spec before implementation, as required by his standing instructions and the spec skill. After approval, start with the minimal two-window positive-control/parity/codec pilot and refresh novelty before expanding.

## 2026-10-05 - Approved implementation begins

- Patrick explicitly confirmed: "i confirm you may begin". The approved spec is now the implementation source of truth.
- Initialized local repository on `feat/ink-fidelity`. GitHub account resolved as pdmacinnes. No commit until verification and a complete coherent deliverable.
- Refreshed compressor HEAD: unchanged at 20b03983ee741baa160d3e630da77a3b3a24ee44; Villa codec PR #1704 still open, updated October 5. Its head is 1630f8ad52289d382adeb688383723aa352679aa.
- Bundled Python 3.12.14 is available; numpy exists, but torch/scipy/Zarr/test dependencies are not installed there. A project-local environment will avoid altering the bundled runtime.

### Environment and first experiments

- Created an isolated environment. Native Windows LLVM-mingw compiler built the pinned upstream volcomp shim as a DLL; no WSL is used. Raw real-CT q=0 round trip is byte-exact.
- GPU arithmetic and released model construction succeed. PyTorch 2.7.1 imported the inference module but failed when building the network because `torch.compiler.disable(reason=...)` was unsupported. Upgraded to official torch 2.11.0+cu128/torchvision 0.26.0+cu128. Exact source modules now work under Python 3.12, despite the full monorepo package's newer declared requirements; this is a validated source adapter, not a claim of supported full-package installation.
- Found an upstream loader using unrestricted pickle. Our adapter instead uses `torch.load(weights_only=True)` and rejects missing/unexpected model keys; released checkpoints load successfully through it.
- Explicit FP32 and TF32-off are used. The pinned upstream run function enters CUDA autocast even with dtype=None; our adapter explicitly passes torch.float32 so autocast is disabled. No upstream source is changed. Baseline model/preprocessing/blending code is reused.
- Initial CT rendering parity failed: MAE 7.207, correlation 0.93396. Nearest-vertex normal sampling alone did not resolve it. C++ source shows even-depth stacks centered at (N-1)/2, not N//2. Corrected 28 layers from offsets [-14,13] to [-13.5,13.5]. Result: correlation 0.999965, float MAE 0.50096; truncating to the renderer's uint8 convention yields MAE 0.00330. The parity gate passes without changing its thresholds or using ink scores.
- Two-window native9 surface-volume pilot completed with both released seeds. Raw repeat and lossless decoded predictions match exactly. q2 losses in AP are small (about 0.0003-0.0014); the padded stream-only ratio against Zstd is about 8x, not yet a complete storage result. q8 worsens some windows more; smoothing is mixed. These windows are on a training-exposed physical segment and cannot establish generalization or readability.
- Selected q2 as the one candidate operating point. Froze 12 separate test windows on six different physical segments across PHerc0139, PHercParis4 and PHerc0841 using only fixed segment IDs and supervision coverage. The latter is an unseen training-scroll stratum, but its annotations are not independent IR ground truth. Threshold and direction follow the frozen protocol.
- Initial tests: 14 passed. Sandbox restrictions on pytest's existing temporary-directory cleanup require a fresh workspace basetemp; rerun with a fresh path and cacheprovider disabled passes. This is an environment permission issue, not a scientific result.
- CT development subwindow initially had one-class supervision and its metric was undefined. The CLI attempted subtraction of undefined scores. Corrected the guard and select two-class subwindows by labels alone before another CT control run; no test manifest is changed.
- First Letters assessment: no qualifying discovery. Current experiments use already-read control scrolls; compression-induced prediction changes are not textual discoveries.

## 2026-10-05 - Frozen results and independent reproduction

- Completed 128 model-arm records on 12 frozen windows, six segment IDs and three scrolls. Raw versus Zstd probabilities are exact; the real native9 CT pipeline completed 16 additional development records after renderer parity.
- q2 actual model-input stores are 3.76-9.90x smaller than the native Zstd comparator, including padding and metadata. Nevertheless, the q2 operating hypothesis is REJECTED: one-sided95 AP bound -0.006067 violates -0.005; worst F1 loss0.04937 violates0.01. Mean AP +0.00805 is not a significant general improvement and does not override adverse cases.
- q8 produces AP losses greater than0.03 on four segments across two scrolls. Largest loss is0.187771 on PHerc0841; another is0.146909 on PHercParis4. This passes the material-failure branch of the approved research gate, with original/lossless input as the demonstrated mitigation. We do not force a universal lossy recommendation or pivot away from useful failure evidence.
- Stage matters: q8-after-depth-pooling versus q8-before-depth-pooling mean deltas differ substantially. The latter encodes the published XY-level2 surface input, not original full-resolution CT. The native9 raw-CT development losses are smaller (largest q8 AP loss0.007405). No whole-mirror certification or condemnation is inferred.
- Cold-source reproduction selected the worst q8 window in each of two physically different scrolls after test scoring. This selection is reproduction, not new held-out evaluation. All24 associated arms match decoded hashes, prediction-file hashes and scores exactly. A second separate-cache reproduction adds direct convolution dtype verification (float32) and OS peak working set2,092,941,312 bytes, and again matches all24 arms.
- Added explicit frame/ROI identity validation, safe filename checks, receipt-based source checks, interrupted-acquisition cleanup and verified resume. Unsafe checkpoint loading is replaced in the adapter with weights_only=True. No upstream source is modified.
- The original pilot manifest before adding a mesh-fetch URL is preserved as pilot-frozen.json, whose hash matches original pilot records. Final frozen-test.json was not changed after prediction scoring.
- Verification:22 package tests,19 upstream flat-inference tests,14 upstream numerical/geometry tests pass; lint passes. Optional upstream test imports required FFT/augmentation/SimpleITK/cc3d/Numba dependencies; these are separated from the minimal inference setup. Earlier import/temporary-directory failures were diagnosed and resolved. Windows setup smoke test passes.
- Static numerical figure inspected visually. No CT, mesh, label, weight or candidate text images are published with the result artifacts.
- First Letters assessment: no discovery and no credible qualifying claim. PHerc0841 has weak raw baselines, and score gains after compression do not establish physical letters. The practical contribution is preventing misleading input-induced negatives in future eligible-scroll searches.
- Next: finalize the evaluation-tool review candidate, commit the verified implementation, and prepare a draft PR. Publication/real community feedback and prize submission remain subsequent actions; no adoption or award is asserted.
- Release check caught Git's automatic JSON line-ending normalization changing the frozen manifest's byte hash. `.gitattributes` now preserves JSON bytes, and staged-blob hashes are checked against measured input manifests before release. This is a packaging correction; no ROI, model, input array or score is changed.
- Resume identity now includes Torch/NumPy/Zarr/CUDA versions and the inference contract; frozen metadata/labels are checksum-enforced by default, and shape changes/renamed physical groups/overlapping scored areas are rejected. Older development cache entries may rerun under this stricter identity. Numerical evidence remains unchanged.

## 2026-10-06 - Public release and fresh setup

- Patrick approved and authorized merging PR #1; merged as9443eba and local main fast-forwarded cleanly. Auto-merge remains OFF.
- Patrick authorized the next stage and pre-approved its spec. Published the reviewed repository and v0.1.0 at16:37UTC. No original CT/labels/meshes/weights or new textual images are included.
- Patrick granted full GPU access for the next90 minutes; the measured work window began16:38UTC and ends approximately18:08UTC (12:08pm America/Denver).
- A genuinely fresh public checkout, new Python environment, source clones, compiler build and model downloads completed successfully on native Windows. The log-display command used the script's changed working directory and failed to locate its own log; the setup itself completed and CUDA/weights/DLL were independently verified.
- Reproduced a public-entrypoint defect in the fresh checkout: `reproduce` defaulted to unpublished local `artifacts/test/results.json`. The baseline algorithm and supplied numerical evidence are valid, but newcomers could not use the shortest command without a full benchmark first.
- Routine patch: reproduction defaults now use the public `reports/benchmark-records.json` and `reports/source-receipts.json`. Explicit local overrides remain supported. Added a regression check that all default reference inputs are shipped files. No scientific parameter or existing reference score changes.
- No external/community messages have been sent. Preparing a reproduction invitation does not establish adoption.

## 2026-10-06 - Fresh release verification completed

- Fresh public Windows setup and the short reproduction command match all24 decoded/probability/metric records exactly. PR #2 repaired the defaults to use shipped reference files;24 package tests and Windows/Linux CI passed. Manually merged the authorized routine release repair as20d343d; published v0.1.1. Auto-merge remains OFF. Anonymous public release access verified.
- Added public numerical reproduction receipts and prepared an unsent reproduction invitation. A second environment on our own PC is not independent community adoption.

## 2026-10-06 - Boundary mechanism hypothesis rejected

- Under Patrick's next-stage spec pre-approval, wrote the padding protocol before scoring. Source inspection identifies existing independent16³ transforms and zero-padded128³ chunks; Zarr's out-of-bounds fill convention is credited, not presented as our discovery.
- H5: the partial transform block in21-plane pooled inputs drives the largest ink failures. Selected the worst published q8 region per Paris4/0841 as explicitly post-test development; evaluated both released seeds, raw/ordinary q8, edge/reflect continuation, raw-tail restoration and tail-only damage.24 records complete.
- Exact q=0/Zstd controls pass for every policy; real voxels remain unchanged before encoding. The first16 decoded planes match across policies. Actual experimental stores read identically with the standard volcomp/Zarr decoder; continuation explicitly differs from the recommended fill-value convention.
- Edge mean AP gain versus zero +0.01383166, worst change -0.01084155; reflect mean +0.01607807, worst -0.03343045. Both fail the prewritten0.01 adverse-case rule. No candidate selected, no fresh-region confirmation run, no threshold relaxed.
- Raw-tail restoration repairs much of Paris4 seed43 AP loss but not0841 seed42. For0841 seed43 it raises AP to0.7252 while F1 at0.5 collapses from0.3878 to0.0050. A boundary-only explanation and an AP-only repair criterion are inadequate. Model response involves interacting perturbations; no stronger physical-causal claim is warranted.

## 2026-10-06 - Normalization counterfactual remains mixed

- H6: recomputed robust patch calibration mediates major q8 damage. Wrote the second protocol after H5 failed and before its inference. Reused the same two exploratory regions, both seeds, official raw normalizer and fixed occupancy;16 records complete. The anchor requires raw reference, so this is diagnostic rather than deployable compression.
- Frozen-raw control predictions are byte-identical to the official raw path. Reference-normalized q8 AP changes versus ordinary q8 are +0.0004/+0.0087 on Paris4 and +0.0031/+0.0265 on0841. The two largest failures remain largely unrepaired;0841 seed42 F1 worsens slightly. No universal normalization repair is supported.
- Guarded final commands were rerun against the default public reproduction inputs. Raw/q8 control hashes are explicitly enforced, all outcomes retained, per-plane/parameter receipts and supervised probability drift included. Final scores match the first24+16 records exactly.
-34 package tests and lint pass locally; native codec integration executes here. Experimental code/results will be a scientific-review draft PR, without merge or new stable release. Original frozen benchmark files remain unchanged.

## 2026-10-06 - First Letters reassessment and next decision

- Read the recent bnleft/first-light-pherc0211 README, pinned to728a27234f50d239c6c83934dad6952b48b94b76. Its authors already test winding sense, second seed, slab profile diagnostics and64-layer tile recentering; their verdict is no convincing ink. These are attributed results, not our reproduction. Another generic centering screen would duplicate their work.
- Rechecked eligible volumes and prize conditions. Existing measured controls are not eligible First Letters targets. PHerc1203 native9 CT exists, but the saved catalog does not expose ready segment properties; a useful screen first needs a verified, source-identified surface on a distinct region.
- No eligible target inference, candidate text publication, speculative tracing/training or outbound message was launched simply to fill GPU time. Next useful step is independent reproduction and feedback on the released evaluator, then a concrete integration into a user's actual workflow. See FIRST_LETTERS_READINESS.md and the unsent invitation.
