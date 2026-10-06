# Spec: Reviewed reliability and mirror release

Status: Patrick reviewed and approved PRs #5/#6/#7 on October6,2026. Release continuation is within his next-stage pre-approval.

## Requirements & Goals

- Merge all three reviewed PRs manually, preserving research logs and negative results when reconciling documentation. Keep auto-merge OFF.
- Release v0.3.0 with the report evidence guard, atomic label-copy repair and bounded actual-mirror probe.
- Preserve every original benchmark/source/model record and conclusion. No new GPU or outbound message is authorized.

## Inputs, Outputs & Behavior

- Inputs: approved code/test commits6941960,38de617,26d7064; immutable v0.2.0 references; existing native codec/models/source pins.
- Outputs: reviewed merged source, updated version/docs,69-test verification, isolated wheel/import check, public source release and code-only wheel.
- Verify merged-tree tests/lint and regenerate the original report summary byte-identically. Build the wheel and validate imports/CLI from its separately installed copy, not the editable source.
- Update reports and handoff status to distinguish reviewed/released code from historical draft observations. Preserve prior audit receipts.

## Edge Cases & Error Handling

- Resolve overlap by preserving both reviewed implementations and all research evidence; do not choose one side wholesale.
- A regression, mismatched numerical summary or package failure blocks publication until repaired and checked.
- Exclude CT/labels/meshes/weights/compiler binaries, credentials and private damaged-input files from release assets.
- The mirror probe certifies only its tested native development crops, and original/lossless input remains the recommendation for evidence-sensitive inference.

## Acceptance Criteria

- [x] All reviewed PRs merged manually with reconciled documentation and passing exact-head CI.
- [x] Merged69 tests and lint pass, and original summary/reference hashes remain unchanged.
- [x] v0.3.0 wheel builds and isolated import/CLI checks pass without GPU.
- [x] README/changelog/feature map/handoff accurately reflect reviewed release and limits.
- [x] Public source tag and code-only wheel verified, with uploaded SHA-256 matching the local artifact.
- [x] No additional outbound message, GPU inference, adoption or First Letters claim.
