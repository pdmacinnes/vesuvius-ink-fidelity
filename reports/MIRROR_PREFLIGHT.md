# Actual public mirror integration - October 6, 2026

**All98 tested native9 CT chunks match local q8 decoding exactly. Both rendered model inputs match the earlier native-CT experiment's published hashes.** This validates a bounded connection to the actual deployed volcomp mirror, using the standard Zarr/Fsspec reader and CPU rendering.

This is format/representation parity on the two PHerc0139-w035 development crops used previously. It does not certify all mirrored volumes, establish new held-out ink performance or recover new text. No model inference was run for this probe.

## Contract and selection

The original and mirror URLs name the same PHerc0139 native9 asset, volume20250728140407, acquisition20250720065842, pitch9.362µm. Both shapes are20974×6621×6621 in z/y/x, with uint8 values. The mirror declares standard Zarrv3 trailing-index shards of1024³, inner128³ chunks and volcomp q8. The original is raw Zarrv2 with128³ chunks.

Before reading mirror values, the [protocol](../specs/mirror-preflight.md) selects first/middle/last sorted global chunk keys from the earlier CT experiment: `(29,22,32)`, `(33,26,33)`, `(41,30,33)`. All three pass, permitting expansion to the98 unique source chunks used by the two existing crops. Selection is based on the earlier sampling geometry, not new predictions. These remain development controls; PHerc0139-w035 appears in model training.

The deployed mirror is read through the existing standard reader. Each decoded chunk is compared with the same global-coordinate original CT chunk and local volcomp q8 reconstruction. Reader-side smoothing is explicitly disabled and restored afterward. Original CT/mesh receipts are enforced. The source mesh is acquired and hash-checked for rendering; arrays/meshes remain Git-ignored.

## Quantitative result and limits

| Check | Result |
|---|---:|
| Actual mirror versus local q8 | 98/98 chunks byte-identical |
| Mirror-rendered versus historical q8 model inputs | 2/2 hashes identical |
| Mirror announced HTTP body bytes | 7,375,909 |
| Original source body bytes fetched in separate cache | 206,436,617 |
| GPU model inference | none |
| Local package tests | 46 passed |

The separate-cache verification fetched the original CT chunks and mesh afresh; the tiny metadata objects had already been verified in the initial format checks. The original acquisition budget is256MiB for expansion; the independent mirror budget is64MiB. Mirror byte accounting sums announced body lengths before reading and excludes HTTP headers/TCP overhead. It is not a codec speed or whole-volume compression benchmark.

The two mirror render hashes are:

| Development crop | Exact model-input SHA-256 |
|---|---|
| w035-dev-a | `d15ea3908a459a1b89769a8d970dd0d4734b5dccb5e4ac939fe940e259942bf7` |
| w035-dev-b | `9dd209379d2ea7e25f81b547799f27eb61991f4ebe8d8afa181aac4532189926` |

These identical inputs connect to the previously measured q8 native-CT arms; the earlier scores are not newly rerun scores. They do not transfer the much larger pooled-input losses onto the entire CT mirror. Local-versus-mirror chunk agreement also does not establish that q8 preserves physical ink everywhere.

## Corrected negative preflights

1. Automatic format detection requested nonexistent v2 metadata from the v3 mirror. Its404 chunked responses lacked explicit lengths, so the guard stopped before data decoding. The probe now requests the independently verified v3 format explicitly.
2. The metadata checker initially treated the standard reader's tuples as different from JSON lists. Semantic sequence normalization fixes this; an added regression test accepts equivalent list/tuple metadata while rejecting changed axes or q values.

Both failures are retained in [negative receipts](mirror-preflight-negatives.json). They were probe implementation/transport issues, not evidence of a corrupt mirror or new codec defect. No failure threshold or numerical baseline was adjusted to force a pass.

## Reproduce

From a prepared source checkout with the pinned native codec and Villa sources:

```powershell
# Full Windows setup supplies the existing HTTP dependencies
.venv\Scripts\ink-fidelity.exe mirror-probe

# All98 registered chunks and both rendered inputs, with a separate source cache
.venv\Scripts\ink-fidelity.exe mirror-probe --expand --cache .cache/mirror-cold
```

The short command reads three chunks. Expansion acquires roughly197MiB of original sources on a cold raw-data cache and about7MiB of announced mirror bodies. It does not load model weights or run GPU kernels. The setup script itself remains the full GPU-workflow setup; this command requires its codec/sources, HTTP dependencies and geometry libraries rather than a model run. Existing fsspec/aiohttp dependencies are now explicitly declared in the `remote` optional extra.

Transport tests reject ignored ranges, wrong offsets/lengths, encoded range bodies, missing lengths and excess budgets, including propagation through the standard HTTP trace callback. Format/option forwarding and shipped default references are tested. Patrick reviewed PR #5; the command is included in v0.3.0. All69 combined release tests pass.

Evidence: [full parity receipt](mirror-preflight.json), [source hashes](mirror-source-receipts.json), [historical CT records](ct-pilot-records.json), [research log](../research/LOG.md). Original benchmark records and v0.2.0 release remain unchanged.
