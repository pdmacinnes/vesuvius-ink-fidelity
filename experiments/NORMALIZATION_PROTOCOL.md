# Normalization counterfactual - October 6, 2026

Written before its model inference. Padding extension candidates failed the registered adverse-case rule, so no fresh confirmation of those policies is run.

Use the same two exploratory worst q8 regions and both fixed seeds. Arms: ordinary raw, ordinary zero-q8, frozen raw reference, and zero-q8 with source-reference normalization. All model/ROI/mask/precision/threshold settings remain unchanged.

The official normalizer's raw output is the anchor. Clip decoded and raw values to the same raw1st/99th percentile bounds; add their difference, expressed in the measured raw affine scale, to the exact official normalized raw tensor. A decoded==raw control therefore exactly reproduces official normalization. Preserve raw occupancy in this counterfactual.

This requires uncompressed reference input and is diagnostic, not a proposed deployable compression policy. Record both successes and failures. A normalization-mediated explanation requires a materially improved score versus ordinary q8 on the previously damaged case, together with unchanged raw-control predictions. Mixed case/seed results imply multiple mechanisms rather than a universal fix.
