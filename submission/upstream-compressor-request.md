# Upstream reproduction request - unsent

Posted with Patrick's explicit authorization as [upstream issue #1](https://github.com/SuperOptimizer/volume-compressor/issues/1), October6,2026. The request below is retained verbatim. No follow-up message has been sent; no independent reproduction or adoption is established.

Proposed title: **Ink-model sensitivity: reproducible pooled-input cases and task evaluation**

---

We released [Vesuvius Ink Fidelity v0.2.0](https://github.com/pdmacinnes/vesuvius-ink-fidelity/releases/tag/v0.2.0), an MIT evaluator reusing volcomp1.3.0 and the released ink_9um seed42/43 models. Your existing model-sensitivity warning motivated the study. This offers concrete ink-label measurements and a bounded reproduction, rather than reporting a new generic codec defect.

On12 frozen windows from six segments across three scrolls, q8 applied to pooled model inputs reduces masked average precision by up to0.18777. Examples:

| Region / seed | Raw AP | q8 AP |
|---|---:|---:|
| PHerc0841 / seed42 | .6826 | .4949 |
| PHercParis4 / seed43 | .9732 | .8263 |

q2 provides3.76-9.90x smaller full stores than native lossless Zstd, but fails our declared AP/F1 budget. Raw/lossless controls are prediction-identical. These are annotation-agreement measurements, not readability or independently established physical ink truth; some regions occur in model training.

**Scope matters:** pooled-input compression, compression before pooling, and original native9 CT compression are distinct experiments. The bounded original-CT -> TIFXYZ -> render -> model experiment has a maximum q8 AP loss of0.00740 on its two development crops. We do not infer these larger pooled-input failures for your whole CT mirror.

The [main report](https://github.com/pdmacinnes/vesuvius-ink-fidelity/blob/v0.2.0/reports/RESULTS.md) supplies models, source hashes, ROI identities, placement comparisons and rejected operating criteria. [Exploratory probes](https://github.com/pdmacinnes/vesuvius-ink-fidelity/blob/v0.2.0/reports/MECHANISMS.md) also test partial-block padding and raw-reference normalization: neither is a reliable repair. One intervention improves AP while F1 at the unchanged threshold collapses, so we retain both measures.

Could you or another interested user try the short reproduction, or suggest a representation/workflow where this paired test would be useful? The documented Windows-native setup requires Python3.12 and a CUDA12.8-compatible NVIDIA GPU; it was tested on an RTX5070Ti. From the prepared repository root:

```powershell
.venv\Scripts\ink-fidelity.exe reproduce
```

It acquires approximately54.6MiB of source objects for two scrolls and checks24 arm predictions/decoded arrays/metrics against the public records. Both an empty-cache run and a fresh Windows environment on our own PC match exactly; an independent reproduction is still wanted. Initial setup also downloads the model weights and large PyTorch runtime.

We would value a mismatch/setup report, advice on integrating task checks into a real compression workflow, or whether linking this evidence from your model-sensitivity documentation would help users. No new letters, universal safe lossy setting or existing external adoption is claimed. The codec, upstream model pipeline and prior sensitivity work are credited.
