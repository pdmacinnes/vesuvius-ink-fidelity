# Spec: Bounded public mirror preflight

Status: within Patrick's pre-approved continued research. This introduces no production reader or model change. New scientific evidence receives a draft PR.

## Requirements & Goals

- Test the actual published volcomp native9 CT mirror through the existing standard Zarr/Fsspec reader, rather than testing only locally encoded arrays.
- Compare identical original global128³ chunk coordinates against original CT and locally encoded/decoded q8. Reuse the pinned codec, source receipts and two prior native-CT development regions.
- Use CPU only. Do not repeat model inference or claim new model/First Letters performance.
- Do not write a new storage engine; use the current `open_array` and standard HTTP tracing to require partial responses and bound transfers before reading shard bodies.

## Inputs, Outputs & Behavior

- Inputs: existing pilot CT URL and acquisition receipts; mirror at the author's documented equivalent path; standard trailing-index Zarrv3 sharding metadata; original native-CT chunk keys and q8 rendered-input hashes.
- Freeze three preflight keys: first, middle and last sorted unique original chunk keys used by the two earlier CT development crops. If all pass, optionally cover the remaining keys and render the same two crops for byte-hash comparison with previously measured q8 inputs.
- Before decoding, require matched shape, uint8 dtype, z/y/x dimensions,128³ inner chunks, q8 codec and the documented mirror path. Keep metadata hashes and source identities.
- Select the already verified Zarrv3 format explicitly. The first guarded attempt found automatic v2 metadata probes yielding404 chunked bodies without lengths; retain that diagnostic rather than weaken the guard.
- Trace standard HTTP requests: any Range request must return206 and a valid Content-Range. Reject a missing length or an aggregate announced transfer above64MiB before consuming the body. This handles the concrete risk of accidentally fetching large whole shards without building a custom store.
- Ship the original CT/mesh source receipts as numerical hashes, so the command does not require unpublished artifacts. Original source acquisition has a separate20MiB preflight budget or256MiB expanded budget; expansion requires about196MiB of original CT on a cold cache. Acquire the original mesh only for expanded rendering.
- Outputs: public numerical receipt with keys, metadata/source hashes, decoded agreement, raw distortion, announced transfer totals and bounded compatibility verdict. Raw arrays remain Git-ignored.
- If full probe inputs match historical q8 rendered hashes, report representation parity only; historical scores are not fresh inference or general mirror certification.

## Edge Cases & Error Handling

- Unsupported/mismatched metadata, ignored ranges, changed receipts, missing/nonfinite data or byte budget violation stops the probe and preserves a negative result.
- Decoder disagreement with local q8 is investigated; do not silently replace the baseline or infer a broad mirror defect from an unexplained sample.
- No training, target candidate screen, outbound message or production recommendation is part of this probe.

## Acceptance Criteria

- [x] Keys and source/frame/codec contract recorded before probe values.
- [x] Three actual mirror chunks compared against original and local q8 through the standard reader, or a precise incompatibility recorded.
- [x] HTTP partial responses and byte budget enforced; no GPU inference used.
- [x] Any expanded render parity is explicitly bounded to the earlier two development crops and hashes.
- [x] Tests for nontrivial transport guards, numerical receipts, research log and draft review PR prepared.
- [x] v0.2.0 and original scientific evidence unchanged; no broad mirror or First Letters claim.
