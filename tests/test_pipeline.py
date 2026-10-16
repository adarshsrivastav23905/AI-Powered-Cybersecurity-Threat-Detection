from __future__ import annotations

import joblib
import pandas as pd
import pytest

from src.alerting import build_alert_summary
from src.data_generation import generate_synthetic_dataset
from src.modeling import save_model, train_and_evaluate
from src.preprocessing import load_and_prepare_data, prepare_features_for_training


@pytest.fixture
def dataset_path(tmp_path):
    path = tmp_path / "data" / "cyber_threat_dataset.csv"
    dataset = generate_synthetic_dataset(path, rows=600)
    return path, dataset


@pytest.fixture
def data_split(dataset_path):
    path, _ = dataset_path
    return load_and_prepare_data(path)


@pytest.fixture
def trained_bundle(data_split):
    X_train, X_test, y_train, y_test, _, _ = data_split
    return train_and_evaluate(X_train, X_test, y_train, y_test)


def test_generator_writes_expected_labeled_dataset(dataset_path):
    path, dataset = dataset_path

    assert path.exists()
    assert len(pd.read_csv(path)) == 600
    assert {"timestamp", "protocol", "attack_type", "label"}.issubset(dataset.columns)
    assert set(dataset["label"]) == {"Normal", "Attack"}


def test_preprocessing_encodes_features_without_target_leakage(dataset_path):
    _, dataset = dataset_path
    features, labels, _, _ = prepare_features_for_training(dataset)

    assert len(features) == len(labels) == len(dataset)
    assert set(labels.unique()) == {0, 1}
    assert "protocol_TCP" in features.columns
    assert not any(
        column in features.columns
        for column in ("label", "attack_type", "severity", "source_ip", "destination_ip")
    )
    assert not features.isna().any().any()


def test_data_split_is_stratified_and_covers_all_rows(data_split):
    X_train, X_test, y_train, y_test, _, _ = data_split

    assert len(X_train) + len(X_test) == 600
    assert len(X_test) == 150
    assert set(y_train.unique()) == {0, 1}
    assert set(y_test.unique()) == {0, 1}
    assert abs(y_train.mean() - y_test.mean()) < 0.02


def test_training_returns_bounded_metrics_and_predictions(data_split, trained_bundle):
    _, X_test, _, y_test, _, _ = data_split

    assert set(trained_bundle) >= {
        "random_forest",
        "isolation_forest",
        "predictions",
        "metrics",
        "cm",
        "anomaly_scores",
    }
    assert len(trained_bundle["predictions"]) == len(y_test)
    assert len(trained_bundle["anomaly_scores"]) == len(X_test)
    assert trained_bundle["cm"].sum() == len(y_test)
    for metric_name in ("accuracy", "precision", "recall", "f1_score"):
        assert 0 <= trained_bundle["metrics"][metric_name] <= 1


def test_alerts_and_saved_model_predictions(data_split, trained_bundle, tmp_path):
    _, X_test, _, y_test, _, dataset = data_split
    alerts = build_alert_summary(
        trained_bundle["random_forest"],
        X_test,
        y_test,
        trained_bundle["isolation_forest"],
        dataset,
    )
    model_path = tmp_path / "threat_model.joblib"
    save_model(trained_bundle["random_forest"], model_path)
    loaded_model = joblib.load(model_path)

    assert len(alerts) <= 10
    assert {"predicted_label", "probability", "anomaly_score", "severity"}.issubset(alerts.columns)
    assert set(alerts["severity"]).issubset({"Critical", "High", "Medium"})
    assert model_path.exists()
    assert (loaded_model.predict(X_test) == trained_bundle["random_forest"].predict(X_test)).all()
