# Copied label cache integrity - October 6, 2026

**The released helper silently retains valid-but-edited copied labels, and retains truncated copied shards that fail on restart. The fix restores both to verified source-exact bytes.** This was reproduced on an isolated copy of the real PHerc0139-w040 label array. Original cache/data/results were not modified.

## Actual-data before/after

Source: PHerc0139-w040 native9 inklabels level0, label revision20260918, shape6400×7980. Trusted source objects are fetched through the existing checksum/receipt path. The isolated copied array has decoded SHA-256:

`b7cda19848dbe5469a3cccf7b625cde91d325cdebc6e200293a28a317a54493c`

| Isolated mutation | Released refresh | Corrected refresh |
|---|---|---|
| Change one positive label through a normal Zarr write | Returns modified labels despite the unchanged verified source | Restores the exact original decoded hash |
| Truncate the copied shard | Skips the existing target; subsequent read fails CRC | Atomically restores source bytes; exact decoded hash recovered |

These are storage integrity experiments, not new label annotations, model-score changes or physical-ink findings. The altered pixel is not presented as a new scored benchmark. [Audit receipt](label-cache-audit.json) contains source hashes and before/after outcomes; arrays remain private/Git-ignored.

## Root cause and repair

The helper verified/acquired the encoded source, but only copied it when the local target did not exist. File existence therefore allowed a stale or partial copied shard to persist. The source-cache checks did not extend to the second copied representation.

Refresh now compares each copied metadata/shard object with the verified source. Matching files are reused. Missing/mismatched targets are streamed to a uniquely named temporary file, flushed, checked against the source hash and atomically replaced. Interrupted writes leave the prior target intact, remove their temporary file and allow a clean retry. Source receipt failures still stop acquisition before touching a good target.

## Verification and limits

- 39 local tests and lint pass on this independent branch. New tests cover valid-but-changed labels, truncated shard/metadata repair, interrupted replacement, healthy reuse and source checksum failure.
- Both real-data corruption cases recover the original decoded hash exactly after refresh. Original trusted source files remain unchanged.
- No GPU, model inference, new annotations, altered supervision threshold or new outbound message was used.

Patrick reviewed PR #7; the fix is included in v0.3.0. All69 combined release tests pass; historical v0.2.0 assets remain unchanged. Hash-exact storage preserves the chosen source labels, not their independent correctness or papyrological truth.
