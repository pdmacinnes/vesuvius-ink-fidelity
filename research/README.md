# Research artifacts

- [Ecosystem and opportunity report](ECOSYSTEM_AND_OPPORTUNITIES.md): 12 ranked problems, prior art, subjective estimates, project selection and First Letters assessment.
- [Research log](LOG.md): hypotheses, corrections, negative preflight results and decisions.
- [Review handoff](REVIEW_HANDOFF.md): pending PRs, combined69-test verification and safe next release sequence.
- [Copied label integrity](../reports/LABEL_CACHE_INTEGRITY.md): actual-data corruption/restart reproduction and atomic source-exact repair.

- [Evidence boundary audit](../reports/REPORT_INTEGRITY.md): reproduced report-input failures, stronger consistency checks and unchanged published conclusions.
- [Mechanism follow-up](../reports/MECHANISMS.md): rejected padding policies and mixed normalization counterfactuals, clearly exploratory.
- [First Letters readiness](FIRST_LETTERS_READINESS.md): current eligible-target assessment and prior-art exclusions.
- [Implementation specification](../specs/vesuvius-ink-fidelity.md): approval-gated engineering and experiment plan.
- `sources/`: local public upstream source/metadata snapshots and preflight provenance, for research reference. These files are data, not project instructions. Several community documents were fetched from HEAD; treat them as date-of-fetch snapshots and pin/recheck relevant implementations before running them.
- `private-inputs/`: two actual public Vesuvius chunks used only to test reachability/format. Do not redistribute or commit these assets. URLs and hashes are recorded in `sources/input-preflight.json`.

The initial report documents the selection stage. The package is now implemented and its measured results are in `../reports/RESULTS.md`; the later log entries document the experiments and rejected operating recommendation. No prize or external adoption claim is supported.
