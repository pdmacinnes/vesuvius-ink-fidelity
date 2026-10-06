# Upstream work and data terms

This package does not implement a new volume codec or ink architecture. It loads unmodified sources from separately acquired upstream checkouts:

- [ScrollPrize/Villa](https://github.com/ScrollPrize/villa), MIT, commit `0e14cf48c8cee74b11e5e40a9d1d520b74e35423`: model construction, patch normalization, depth selection, inference/blending and TIFXYZ geometry helpers.
- [SuperOptimizer/volume-compressor](https://github.com/SuperOptimizer/volume-compressor), MIT, commit `20b03983ee741baa160d3e630da77a3b3a24ee44`: volcomp1.3.0 codec, ctypes interface and Zarr serializer. Its existing CT and surface-teacher benchmarks are prior art, not our contribution.
- [LLVM-mingw](https://github.com/mstorsjo/llvm-mingw), portable Windows compiler, release20260922 ucrt-x86_64. Its own licenses apply; binaries are not distributed here.
- [fsspec](https://github.com/fsspec/filesystem_spec), BSD-3-Clause, and [aiohttp](https://github.com/aio-libs/aiohttp), Apache-2.0 AND MIT according to the installed3.12.15 metadata: existing standard HTTP transport and request tracing. The optional remote extra records the validated2025.9.0/3.12.15 versions; their sources are not bundled.

Upstream notices remain in their checkouts. No upstream source, binary, data or model weight is bundled in this repository.

Vesuvius data and label assets have their own licenses and [data-server terms](https://dl.ash2txt.org/LICENSE.txt). The selected catalog entries identify CC BY-NC4.0; the server terms also restrict redistribution and textual disclosures. Fetch originals from their existing hosts. This repository releases numerical experiment records and source manifests, excluding CT, mesh/label arrays, weights and candidate textual images. If using EduceLab-Scrolls, cite Parsons et al., [arXiv:2304.02084](https://arxiv.org/abs/2304.02084) as required by the source terms.

Released [ink_9um weights](https://huggingface.co/scrollprize/ink_9um) are MIT according to their model card. We record their SHA-256 and load them using restricted weight loading.
