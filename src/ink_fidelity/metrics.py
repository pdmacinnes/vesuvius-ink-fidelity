from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score


def ink_metrics(labels, probabilities, supervision, *, threshold: float) -> dict:
    labels, probabilities, supervision = map(np.asarray, (labels, probabilities, supervision))
    if labels.shape != probabilities.shape or labels.shape != supervision.shape:
        raise ValueError("Labels, prediction and supervision must have identical shapes")
    if not np.isfinite(probabilities).all():
        raise ValueError("Non-finite prediction")
    if np.any((probabilities < 0) | (probabilities > 1)):
        raise ValueError("Probabilities must be in [0,1]")
    if not 0 <= threshold <= 1:
        raise ValueError("Threshold must be in [0,1]")
    y = labels[supervision > 0] > 0
    p = probabilities[supervision > 0]
    result = {"pixels": len(y), "positives": int(y.sum()), "negatives": int((~y).sum())}
    if not len(y) or not y.any() or y.all():
        return {
            **result,
            "defined": False,
            "reason": "empty or one-class supervision",
            "average_precision": None,
            "roc_auc": None,
            "f1": None,
        }
    pred = p >= threshold
    tp = int(np.sum(pred & y))
    fp = int(np.sum(pred & ~y))
    fn = int(np.sum(~pred & y))
    return {
        **result,
        "defined": True,
        "average_precision": float(average_precision_score(y, p)),
        "roc_auc": float(roc_auc_score(y, p)),
        "f1": 2 * tp / (2 * tp + fp + fn),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "threshold": threshold,
    }


def prediction_drift(reference, candidate, valid, *, threshold: float) -> dict:
    reference, candidate, valid = map(np.asarray, (reference, candidate, valid))
    if reference.shape != candidate.shape or valid.shape != reference.shape:
        raise ValueError("Prediction drift arrays must share a shape")
    if not np.isfinite(reference).all() or not np.isfinite(candidate).all():
        raise ValueError("Non-finite prediction")
    a, b = reference[valid > 0], candidate[valid > 0]
    if not len(a):
        raise ValueError("Empty valid area")
    pa, pb = a >= threshold, b >= threshold
    denom = int(pa.sum() + pb.sum())
    return {
        "mean_abs_probability_difference": float(np.abs(a - b).mean()),
        "p99_abs_probability_difference": float(np.quantile(np.abs(a - b), 0.99)),
        "prediction_dice": float(2 * np.sum(pa & pb) / denom) if denom else None,
        "raw_foreground": int(pa.sum()),
        "candidate_foreground": int(pb.sum()),
        "lost_raw_foreground": int(np.sum(pa & ~pb)),
        "new_foreground": int(np.sum(~pa & pb)),
    }


def grouped_delta_interval(rows: list[dict], *, metric="delta_ap", seed=42, repeats=10000) -> dict:
    groups = {}
    for row in rows:
        if row.get(metric) is not None:
            groups.setdefault(row["physical_segment"], []).append(float(row[metric]))
    means = np.array([np.mean(v) for _, v in sorted(groups.items())])
    if len(means) < 3:
        return {
            "groups": len(means),
            "mean": float(means.mean()) if len(means) else None,
            "lower95_one_sided": None,
            "ci95": None,
            "verdict": "inconclusive",
        }
    rng = np.random.default_rng(seed)
    boot = means[rng.integers(len(means), size=(repeats, len(means)))].mean(axis=1)
    return {
        "groups": len(means),
        "mean": float(means.mean()),
        "lower95_one_sided": float(np.quantile(boot, 0.05)),
        "ci95": np.quantile(boot, [0.025, 0.975]).tolist(),
    }
