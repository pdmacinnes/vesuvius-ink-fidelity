# Evidence boundary audit - October 6, 2026

**Two malformed tables were accepted by the released reporter; both are now rejected before report writes. All128 published records pass the stronger checks, and the regenerated numerical summary is byte-identical.** The original model measurements and conclusions need no correction.

## Reproduced failures

The audit uses private damaged copies of the actual public Vesuvius benchmark records. Original data/results are not modified, and no model inference runs.

| Damaged input | v0.2.0 behavior | Corrected behavior |
|---|---|---|
| Replace one Zstd cell with a duplicate q8 cell under a new run ID | Accepts128 rows and claims completeness | Rejects duplicate experiment cell; no output directory created |
| Replace every q8 AP delta with its absolute value, leaving recorded AP unchanged | Accepts table; reported material-failure segments fall from4 to0 | Rejects paired AP arithmetic mismatch; no output directory created |

Both cases were exercised through the actual console entrypoint, as well as the report API. The older independently installed source has the same released reporter; it accepts both. The corrected CLI exits1 for each. [Audit receipt](report-integrity-audit.json) records outcomes and immutable source hashes. Damaged inputs and their misleading baseline reports remain private under `.cache/`.

## Root cause and repair

The old completeness check required the expected total count and unique run IDs. A run ID is a configuration identity, not an experiment-cell key. Those conditions do not prove that every declared window/seed/arm is present once. Separately, gate/interval computation trusted supplied delta fields without checking them against the recorded raw and candidate metrics.

The new validation derives the exact matrix from the frozen manifest and requires each expected cell once. It checks physical/sample/placement identities, manifest hashes, pinned model/source/inference conventions, paired input/support/runtime consistency, supervision counts, finite metrics, confusion-count/F1 arithmetic, storage ratio arithmetic and AP/F1 deltas against raw anchors.

Lossless inputs must be byte-exact; the producer's existing1e-6 prediction tolerance remains unchanged. A claimed zero prediction difference additionally requires identical probability hashes and metrics. Stored floating arithmetic uses1e-12 absolute tolerance. Undefined or malformed scored evidence is rejected; missing measurements are never fabricated. Validation runs before plotting imports or output-directory creation.

A small but complete one-segment manifest now returns an explicit inconclusive interval and fails the operating gate instead of crashing on a missing confidence bound. This synthetic subset is a software check, not a newly preregistered scientific evaluation.

## Verification and limits

- 52 local tests and lint pass. Regressions use the actual public records and exercise missing/duplicate/unknown cells, changed source/placement/seed/model/runtime fields, nonfinite or inconsistent metrics, storage ratios and lossless controls.
- Valid full-table report regeneration matches the original numerical summary byte-for-byte. The q2 gate remains rejected and four q8 material-failure segments remain identified.
- The two damaged console cases fail with actionable messages and produce no new report artifacts.
- GPU inference, source/model weights and statistical threshold/bootstrap rules are unchanged. Original benchmark, manifest and summary files remain immutable.

These checks enforce consistency and protocol boundaries; they do not authenticate arbitrary self-consistent fabricated data or establish physical ink truth. Probability/source reproduction remains a separate control. Patrick reviewed PR #6; the fix is included in v0.3.0. All69 combined release tests pass. Historical v0.2.0 assets remain unchanged.
