# Feature map

| Feature | Implementation | Evidence/status |
|---|---|---|
| Public bounded acquisition | `acquisition.Fetcher`, `RemoteV2Array` | Real CT/surface/label chunks acquired; checksums, byte budget, transient retry, truncation and shape checks. Raw v2 volume path rejects unsupported filters/dtypes. |
| Standard Zarr input | `acquisition.open_array`, label mirror | Local arrays and OME groups v2/v3 tested. Explicit levels required; actual v3 labels and v2 CT/surface used. |
| Upstream codec reuse | `compression.Codec` | Native Windows DLL built from pinned upstream; real q=0 and Zstd round trips exact. No new codec. |
| Official ink model adapter | `inference.InkModel` | Both released seeds run on RTX5070Ti; restricted checkpoint loading, strict state match, FP32/TF32-off and captured float output. |
| CT -> TIFXYZ render | `rendering.render_surface`, CLI `ct` | Uses upstream geometry helpers; half-voxel layer center and nearest vertex normals. Published-render control correlation0.999965 and byte MAE0.00330 on first probe. |
| Development pilot | CLI `pilot`, `experiments/pilot.json` | Two windows × two seeds × six arms complete; raw repeat and lossless predictions exact. |
| Test selection | CLI `freeze`, `selection` | Twelve windows on six segments/three scrolls frozen using label coverage only, no prediction selection. |
| Frozen benchmark | CLI `benchmark`, `benchmark` | Complete: 128 records, 12 windows, six segments, three scrolls, both seeds; native/pooled arms and actual codec store accounting. |
| Honest metrics | `metrics` | Masked AP/ROC-AUC/F1; undefined one-class scores explicit; physical-segment grouped intervals. Unit tests pass. |
| Verified resume | `benchmark`, `validation` | Matching run identity/checksum required; corrupt/missing/changed artifacts and interrupted acquisitions tested. Source receipts enforced during cold reproduction. |
| Export/report | CLI `report`, `quality` | JSON/CSV/PNG evidence complete; q2 operating gate rejected, q8 material-failure gate passed. No readability claims. |
| Report evidence boundary | `validation.validate_report_rows`, `report` | Review candidate: exact experiment matrix, source/model/paired arithmetic and control checks. Two reproduced malformed-table failures rejected; all128 public records validate and summary remains byte-identical. |
| Cold reproduction | CLI `reproduce` | Two separate source caches; 24 model arms each; exact input/output/score equality on failures from two different scrolls. Direct FP32 convolution and OS peak-RAM evidence captured. |
| Fresh public installation | Published v0.1.1; `reports/public-install-reproduction.json` | New Windows checkout/environment/compiler/models; documented short command reproduces all24 public records exactly. PR #2 fixed unpublished default input paths. This is local reproduction, not external adoption. |
| Boundary mechanism probes | CLI `padding-study`, `padding_study`, `Codec.pad_chunk` | Reviewed exploratory40-record follow-up with normalization; both edge/reflect policies fail the prewritten adverse-case rule. Standard-reader compatibility and exact lossless controls checked. Experimental writer is not a recommended storage policy. |
| Raw-reference normalization | CLI `normalization-study`, `normalization_study` | Bit-identical official raw controls; diagnostic requires source input. Largest losses remain. Wrapper restoration after inference failure tested. |
| First Letters assessment | `research/FIRST_LETTERS_READINESS.md` | No new discovery; PHerc0211 centering/second-seed work already exists. No target screen launched without a distinct, verified surface/problem. |

Current project status: v0.2.0 is public at152bb99. Actual-mirror integration awaits review in draft PR #5; this separate branch hardens the report evidence boundary. The authorized upstream reproduction request is posted as compressor issue #1. Auto-merge is OFF. External adoption and actual prize submission remain pending.
