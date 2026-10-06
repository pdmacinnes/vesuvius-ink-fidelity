# Spec: Reviewed diagnostic release and upstream handoff

Status: Patrick approved the research PR and continued work on October6,2026. Covered by his earlier next-stage spec pre-approval. Outbound community messages still require explicit authorization.

## Requirements & Goals

- Merge reviewed PR #3 with auto-merge OFF and publish v0.2.0 containing the reviewed diagnostic commands and their negative results.
- Preserve original benchmark records, frozen manifest, source/model pins and conclusions. The experimental writer is available only as a research diagnostic, not a recommended compression policy.
- Verify package construction and CPU-only command imports without consuming GPU after the expired authorization window.
- Refresh upstream novelty and prepare a concrete, technically scoped reproduction/integration request. Do not post it without Patrick's explicit permission.

## Inputs, Outputs & Behavior

- Inputs: reviewed PR #3, v0.1.1 evidence, fixed study protocols/records, public upstream repository/PR state.
- Outputs: v0.2.0 source release and wheel, updated version/README/changelog/feature map, release checks and an unsent upstream request.
- Work on a separate release branch/PR, run existing tests and lint, build the wheel, install it into an isolated directory and verify that its commands/imports resolve to that installed copy.
- Document that this research package runs from a repository checkout with separately acquired sources/assets; the wheel alone is not a standalone data/model bundle.
- Check standard numerical artifact hashes and exclusion of CT/labels/weights/secrets from the wheel and release source.

## Edge Cases & Error Handling

- A clean package or command-import failure is reproduced and repaired before release. Never silently use the editable local source as the isolated-install control.
- Packaging must retain module entrypoints and version while excluding original data. No new dependencies or GPU inference are required for this stage.
- Existing upstream sensitivity warnings are credited; distinguish pooled model-input measurements from whole CT-mirror claims.
- Missing community authorization leaves the request unsent; no adoption claim is inferred from publication or our own reproduction.

## Acceptance Criteria

- [x] Reviewed PR #3 merged manually; auto-merge remains OFF.
- [x] v0.2.0 version/docs identify reviewed diagnostics and negative outcomes accurately.
- [x] Existing34 local tests, lint and Windows/Linux CI pass.
- [x] Built wheel installs in isolation and its CLI/import/version smoke checks pass without GPU.
- [x] Original numerical records/manifests remain byte-identical; release assets exclude raw data/weights/secrets.
- [x] Public source release and wheel are available at a verified tag/commit.
- [x] Upstream novelty/integration evidence and a concrete request are recorded; no unauthorized message is sent.
