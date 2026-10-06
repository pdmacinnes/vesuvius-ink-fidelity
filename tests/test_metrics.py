import numpy as np
import pytest

from ink_fidelity.metrics import grouped_delta_interval, ink_metrics, prediction_drift


def test_known_ranking_and_ties():
    labels = np.array([1, 0, 1, 0])
    result = ink_metrics(labels, np.array([0.9, 0.8, 0.7, 0.6]), np.ones(4), threshold=0.75)
    assert result["average_precision"] == pytest.approx(5 / 6)
    assert result["roc_auc"] == 0.75
    assert result["f1"] == 0.5
    tied = ink_metrics(labels, np.full(4, 0.5), np.ones(4), threshold=0.5)
    assert tied["average_precision"] == 0.5
    assert tied["roc_auc"] == 0.5


def test_unknown_pixels_are_not_negatives():
    result = ink_metrics(
        np.array([1, 0, 0]), np.array([0.9, 0.8, 1.0]), np.array([1, 1, 0]), threshold=0.85
    )
    assert result["pixels"] == 2
    assert result["f1"] == 1


@pytest.mark.parametrize("labels,mask", [([0, 1], [0, 0]), ([1, 1], [1, 1]), ([0, 0], [1, 1])])
def test_undefined_scores_are_explicit(labels, mask):
    result = ink_metrics(np.array(labels), np.array([0.2, 0.7]), np.array(mask), threshold=0.5)
    assert not result["defined"]
    assert result["average_precision"] is None


def test_nonfinite_and_mismatched_inputs_fail():
    with pytest.raises(ValueError, match="Non-finite"):
        ink_metrics(np.array([0, 1]), np.array([0.1, np.nan]), np.ones(2), threshold=0.5)
    with pytest.raises(ValueError, match="identical"):
        ink_metrics(np.ones(2), np.ones(3), np.ones(2), threshold=0.5)


def test_prediction_agreement_empty_foreground_is_undefined():
    result = prediction_drift(np.zeros(3), np.zeros(3), np.ones(3), threshold=0.5)
    assert result["prediction_dice"] is None
    assert result["new_foreground"] == 0


def test_grouping_avoids_counting_windows_or_seeds_as_independent():
    rows = [{"physical_segment": "a", "delta_ap": 0.1}] * 100
    rows += [
        {"physical_segment": "b", "delta_ap": -0.1},
        {"physical_segment": "c", "delta_ap": 0.0},
    ]
    result = grouped_delta_interval(rows)
    assert result["groups"] == 3
    assert result["mean"] == pytest.approx(0, abs=1e-12)
    assert result == grouped_delta_interval(rows)
    assert grouped_delta_interval(rows[:100])["verdict"] == "inconclusive"
