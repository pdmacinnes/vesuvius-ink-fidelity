# Reproduction invitation - unsent draft

Status: this broader invitation remains unsent. A focused request was posted with Patrick's authorization as [compressor issue #1](https://github.com/SuperOptimizer/volume-compressor/issues/1). Any additional destination/message needs separate authorization.

We released [Vesuvius Ink Fidelity](https://github.com/pdmacinnes/vesuvius-ink-fidelity/releases/tag/v0.1.1), a small MIT evaluator that reuses volcomp and the released ink_9um models to measure paired ink-label sensitivity through pooling/rendering and inference.

The main finding is a reproducible adverse case: q8 on pooled model input loses up to0.188 masked average precision, and even q2 fails our declared AP/F1 operating budget. This does not assess the whole compressed CT mirror; the bounded native9 CT rendering experiment has much smaller losses. The codec's existing CT-image/surface-teacher work and model-sensitivity warning are credited.

Could someone try the documented native Windows setup and short `ink-fidelity reproduce` command, or run the evaluator on a representation they actually use? It downloads a bounded two-scroll subset and compares24 arm predictions and metrics with the supplied records. A clean environment on our own PC matched all24 exactly, but we would value a genuinely independent check and feedback on useful integration points.

Please report setup failures, mismatches and domain/representation details. We are especially interested in whether the adverse cases alter a practical storage/inference decision. We have no new letters or universal lossy recommendation, and no community adoption claim yet.
