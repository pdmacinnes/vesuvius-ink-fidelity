from __future__ import annotations

import argparse
import logging
from pathlib import Path

LOGGER = logging.getLogger(__name__)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Vesuvius ink fidelity experiments")
    sub = parser.add_subparsers(dest="command", required=True)
    run = sub.add_parser("pilot")
    run.add_argument("--manifest", type=Path, default=Path("experiments/pilot.json"))
    run.add_argument("--out", type=Path, default=Path("artifacts/pilot"))
    run.add_argument("--seed", type=int, choices=[42, 43], default=42)
    run.add_argument("--render-only", action="store_true")
    freeze = sub.add_parser("freeze")
    freeze.add_argument("--catalog", type=Path, default=Path("research/sources/catalog.json"))
    freeze.add_argument("--out", type=Path, default=Path("experiments/frozen-test.json"))
    bench = sub.add_parser("benchmark")
    bench.add_argument("--manifest", type=Path, default=Path("experiments/frozen-test.json"))
    bench.add_argument("--out", type=Path, default=Path("artifacts/test"))
    bench.add_argument("--cache", type=Path, default=Path(".cache/http"))
    bench.add_argument("--receipts", type=Path)
    ct = sub.add_parser("ct")
    ct.add_argument("--manifest", type=Path, default=Path("experiments/pilot.json"))
    ct.add_argument("--out", type=Path, default=Path("artifacts/ct-pilot"))
    summary = sub.add_parser("report")
    summary.add_argument("--results", type=Path, default=Path("artifacts/test/results.json"))
    summary.add_argument("--manifest", type=Path, default=Path("experiments/frozen-test.json"))
    summary.add_argument("--out", type=Path, default=Path("reports"))
    repeat = sub.add_parser("reproduce")
    repeat.add_argument("--results", type=Path, default=Path("reports/benchmark-records.json"))
    repeat.add_argument("--manifest", type=Path, default=Path("experiments/frozen-test.json"))
    repeat.add_argument("--receipts", type=Path, default=Path("reports/source-receipts.json"))
    repeat.add_argument("--cache", type=Path, default=Path(".cache/cold-reproduction"))
    repeat.add_argument("--out", type=Path, default=Path("artifacts/reproduction"))
    quality = sub.add_parser("quality")
    quality.add_argument("--results", type=Path, default=Path("artifacts/test/results.json"))
    quality.add_argument("--artifacts", type=Path, default=Path("artifacts/test"))
    quality.add_argument("--out", type=Path, default=Path("reports/model-input-quality.json"))
    padding = sub.add_parser("padding-study")
    padding.add_argument("--results", type=Path, default=Path("reports/benchmark-records.json"))
    padding.add_argument("--manifest", type=Path, default=Path("experiments/frozen-test.json"))
    padding.add_argument("--artifacts", type=Path, default=Path("artifacts/reproduction"))
    padding.add_argument("--out", type=Path, default=Path("artifacts/padding-development"))
    normalization = sub.add_parser("normalization-study")
    normalization.add_argument(
        "--results", type=Path, default=Path("reports/benchmark-records.json")
    )
    normalization.add_argument(
        "--manifest", type=Path, default=Path("experiments/frozen-test.json")
    )
    normalization.add_argument("--artifacts", type=Path, default=Path("artifacts/reproduction"))
    normalization.add_argument(
        "--out", type=Path, default=Path("artifacts/normalization-development")
    )
    mirror = sub.add_parser("mirror-probe")
    mirror.add_argument("--manifest", type=Path, default=Path("experiments/pilot.json"))
    mirror.add_argument("--reference", type=Path, default=Path("reports/ct-pilot-records.json"))
    mirror.add_argument("--out", type=Path, default=Path("artifacts/mirror-preflight"))
    mirror.add_argument(
        "--receipts", type=Path, default=Path("reports/mirror-source-receipts.json")
    )
    mirror.add_argument("--cache", type=Path, default=Path(".cache/http"))
    mirror.add_argument("--expand", action="store_true")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    logging.basicConfig(level=logging.WARNING)
    try:
        if args.command == "mirror-probe":
            from .mirror_probe import mirror_probe

            mirror_probe(
                args.manifest,
                args.reference,
                args.out,
                receipts_path=args.receipts,
                cache=args.cache,
                expand=args.expand,
            )
        elif args.command == "normalization-study":
            from .normalization_study import normalization_study

            normalization_study(args.results, args.manifest, args.artifacts, args.out)
        elif args.command == "padding-study":
            from .padding_study import padding_study

            padding_study(args.results, args.manifest, args.artifacts, args.out)
        elif args.command == "freeze":
            from .selection import freeze_manifest

            freeze_manifest(args.catalog, args.out)
        elif args.command == "ct":
            from .ct_experiment import ct_experiment

            ct_experiment(args.manifest, args.out)
        elif args.command == "quality":
            from .quality import model_input_quality

            model_input_quality(args.results, args.artifacts, args.out)
        elif args.command == "reproduce":
            from .reproduction import reproduce

            reproduce(args.results, args.manifest, args.out, args.cache, args.receipts)
        elif args.command == "report":
            from .report import report

            report(args.results, args.manifest, args.out)
        elif args.command == "benchmark":
            import json

            from .benchmark import benchmark

            receipts = (
                json.loads(args.receipts.read_text(encoding="utf-8")) if args.receipts else None
            )
            benchmark(args.manifest, args.out, cache=args.cache, receipts=receipts)
        else:
            from .experiment import pilot

            pilot(args.manifest, args.out, render_only=args.render_only, seed=args.seed)
    except Exception:
        LOGGER.exception("Experiment failed; no complete result claimed")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
