# Pilot protocol

Approved direction: ink sensitivity to compression. Frozen before first real ink predictions, October 5, 2026.

The pilot uses two supervised windows on one physical PHerc0139 segment. It is development evidence only. Selection used supervision coverage on a fixed grid and no model output. A 128-pixel halo surrounds each scored 512-square window; all crop origins align to the original 128-pixel chunk grid and 64-pixel inference grid.

Raw CT rendering parity is evaluated before lossy raw-CT comparisons. The first geometry probe uses a 128-square part of a development window, 28 normal samples, flipped normals as recorded in the catalog. Match correlation must exceed 0.98 and MAE must be below 2 intensity units against the published surface, allowing only justified renderer quantization. If it fails, diagnose coordinate/depth conventions with CT-only comparisons, never with ink scores.

CT-only convention correction: the initial offsets -14 to +13 failed parity. Inspection of the C++ `buildOffsetList` establishes center=(N-1)/2, hence offsets -13.5 to +13.5 for 28 layers. Linear rendering uses nearest stored-vertex normals. Correct these from source evidence, without inspecting ink results or moving the parity thresholds.

Pilot inference: official fixed final seed42 and seed43 ink_9um weights; full precision with TF32 disabled; stride 64, Hann overlap blending, centered 17 slices, forward depth orientation. Capture float output before the upstream uint8 export. Threshold 0.5 is only an exploratory development threshold, not a final recommendation.

Arms: raw; lossless Blosc/Zstd; volcomp q=2,4,8; one q=8 upstream gated smoothing arm. Model weights, geometry, masks, preprocessing and inference settings are identical in paired arms. First run raw twice. Lossless decoded voxels must be bit-identical and float predictions must be identical within a maximum tolerance 1e-6.

No submission follows from this pilot. A final operating recommendation needs a separate frozen manifest with independent physical segments, grouped uncertainty, raw baseline quality and reported adverse effects.
