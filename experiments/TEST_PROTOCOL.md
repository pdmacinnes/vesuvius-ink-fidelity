# Frozen test protocol

Freeze this protocol and the generated manifest before model predictions on its regions.

The development pilot on w035 passes raw/repeat/lossless controls. Across both seeds and both windows, q2 is the selected candidate: it has the smallest observed AP loss among tested lossy qualities and approximately eight times fewer stream bytes than the matched padded Zstd control. Those stream ratios omit metadata, and no storage claim is accepted until actual store sizes are included. q8 is a diagnostic comparator, never selected per test window.

Test targets are fixed in `selection.TARGETS`: two PHerc0139 segments, two PHercParis4 segments and two PHerc0841 segments, all separate from pilot w035. A deterministic label-only selector chooses two 256-square scored windows per segment, with a 128-pixel halo and at least 512 pixels separating scored window origins along one axis. Eligibility requires at least 100 positives and negatives and 2,000 supervised pixels. This deliberately samples supervised ink regions, not the distribution of the whole scroll.

Native9 representations are used directly. Fine-pitch representations use the published level-2 XY pyramid, the official centered 84 planes, and rounded mean of groups of four planes to produce 21 slices. The manifest records source shape and label level. PHerc0841 direction is reverse based on the existing public transfer benchmark; no test-label orientation search is allowed.

Arms for native9: raw, Zstd, q2, q8. For pooled input add q2-before-depth-pooling and q8-before-depth-pooling. Only one candidate operating point (q2) is selected. Lossless values/output must match raw. Model seeds, threshold 0.5, FP32/TF32-off, stride64 and Hann blending remain fixed.

Analyze AP/Dice changes by physical segment and seed, report raw baseline quality, and use grouped bootstrap by physical segment. Success criteria are those in the approved spec. In particular, a storage recommendation needs >=2x lower fully accounted bytes, AP lower one-sided95 bound >=-0.005, no segment AP drop worse than0.02, and F1 drop <=0.01. Weak baselines and pseudo-label accuracy cannot establish legibility. Failure of this gate is recorded, not hidden by averaging.

Independent raw-CT before-render evidence uses development windows after raw-render parity. It is a separate placement experiment and does not make model-input compression results into a raw-mirror certification.
