# Spec: Public release and reproduction readiness

Status: pre-approved by Patrick on October 6, 2026: "feel free to start the next step" and "i will pre approve the spec". The existing scientific contract and frozen results remain authoritative.

## Requirements & Goals

- Publish the reviewed, merged v0.1.0 repository and prepared GitHub release; preserve auto-merge OFF.
- Verify anonymous public access and a genuinely fresh Windows installation, rather than relying on the already prepared environment.
- Make the shortest independent reproduction path usable from the public repository alone. Fix concrete setup/documentation/entrypoint blockers on a branch with a PR and passing checks.
- Preserve the published ROI set, model weights, preprocessing, precision, supervision semantics, metrics, thresholds and scientific conclusions. Record any discovered issue and its effect on existing evidence.
- Prepare an independent reproduction request and submission-readiness summary. Do not send community messages without explicit outbound authorization; do not claim an external reproduction from another run on our own PC.
- Keep raw CT/mesh/label arrays, weights and potential new text excluded from published Git/release assets.
- If a scientific correctness issue appears, fix and revalidate it, retaining the original negative evidence and a transparent correction. Material changes to the evaluation method receive human review; routine release/setup fixes are within this pre-approved next stage.

## Inputs, Outputs & Behavior

- Inputs: merged commit9443eba, existing release draft, public frozen manifests/reference records/source receipts, reviewed source pins and the local Windows/RTX5070Ti hardware.
- Outputs: public repository and versioned release; fresh-install and reproduction receipts; usable short commands; documented release status; PR for any necessary fixes; unsent outreach and October submission drafts.
- Publish v0.1.0, verify its actual visibility/tag/commit and anonymous access, and retain that version's evidence.
- Clone public source into an isolated scratch directory, create a fresh environment, build the native codec, acquire checksum-pinned weights and run the documented reproduction/control path.
- Compare reproduced outputs against published numerical records. A separate local environment is a packaging/reproducibility check, not community adoption or new held-out research.
- Repair only demonstrated blockers; reuse existing acquisition/inference/codec functionality. Do not add a workflow service or unrelated features.
- Release a patch version if fixes are necessary, with a concrete changelog and unchanged scientific conclusions when verified.
- Check current relevant upstream work and prepare a concise reproduction invitation for the codec/Villa community, held as a draft.

## Edge Cases & Error Handling

- Missing local artifacts on a fresh clone: use the reference results and receipts already published in `reports/`, or require explicit paths with actionable errors.
- Missing or incompatible runtime/compiler/GPU: report supported versions and the precise failing step; do not silently select a different model, precision or pipeline.
- Partial downloads, bad hashes, dirty/wrong upstream pins and changed source shapes: fail safely, preserve diagnostic evidence and use the existing verified acquisition path.
- Git line-ending or archive changes: check byte hashes on fresh public checkout/release archive, especially frozen JSON manifests.
- Any result mismatch: diagnose before public performance/fidelity claims; distinguish packaging errors from scientific errors and document corrections.
- No external feedback yet: keep adoption status unclaimed. Draft messages without posting or emailing them.

## Acceptance Criteria

- [ ] Repository is publicly accessible and v0.1.0 points to the reviewed merged commit.
- [ ] Auto-merge remains OFF; publication contains only the approved source/numerical artifacts.
- [ ] A fresh native Windows environment builds the pinned codec and loads both released models through the documented setup.
- [ ] A public-reference reproduction command works without first producing the full private/local benchmark directory.
- [ ] Frozen manifest hashes and selected reproduced inputs/probabilities/metrics match the published evidence, or any discrepancy is explicitly corrected and revalidated.
- [ ] Relevant tests, lint, setup syntax and CI pass for any patch; changes follow branch/PR conventions.
- [ ] Release notes, feature map and research log accurately distinguish reviewed release, local reproduction and actual external adoption.
- [ ] Outreach and submission drafts are concrete and unsent; no First Letters finding or prize outcome is claimed.
