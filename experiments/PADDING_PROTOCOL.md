# Padding mechanism protocol - October 6, 2026

Written before running the padding variants. This is a post-test exploratory mechanism study, not a reclassification of v0.1's scored regions as held out.

Use the worst q8 region in PHercParis4 and PHerc0841 from the published records. Evaluate both fixed released model seeds at unchanged FP32, stride64, Hann blending, centered17 depth planes and threshold0.5.

Arms: raw, existing zero-padded q8, edge-to-next16-block q8, reflect-to-next16-block q8, zero-q8 with raw boundary planes restored, and raw with only the zero-q8 boundary planes substituted. A21-plane stack has a complete first16-plane block and a partial second block. Verify that changed padding leaves the decoded complete block bit-identical.

Measure AP/F1, raw agreement, per-plane error, actual codec store bytes and standard-reader equality. Raw predictions must match published hashes. Extension policies must preserve real voxels before compression and q=0/Zstd exact controls. Encoded stores declare the real array shape; unused boundary values are not model input. Continuation beyond array bounds explicitly differs from Zarr's recommended fill-value convention and remains experimental.

Choose at most one extension policy using mean AP improvement versus zero-q8 across the four development window/seed cells. Require a positive mean and no cell worsened by more than0.01 AP before proceeding to fresh-region confirmation. A causal-tail interpretation additionally requires substantial recovery with raw boundary restoration; otherwise record a weaker/negative mechanism conclusion.

Fresh confirmation is separately frozen after development selection and before its predictions. Its named segments/regions must not occur in the primary or exploratory study. All successes and failures are retained. No extension policy is labeled universally safe, and AP remains annotation agreement rather than verified recovered letters.
