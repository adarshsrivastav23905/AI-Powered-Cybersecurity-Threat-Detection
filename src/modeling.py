from __future__ import annotations

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, precision_recall_fscore_support
from sklearn.ensemble import IsolationForest


def train_classifier(X_train, y_train):
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        min_samples_leaf=2,
    )
    model.fit(X_train, y_train)
    return model


def train_anomaly_detector(X_train):
    model = IsolationForest(
        contamination=0.12,
        random_state=42,
        n_estimators=200,
    )
    model.fit(X_train)
    return model


def evaluate_model(model, X_test, y_test):
    predictions = model.predict(X_test)
    accuracy = accuracy_score(y_test, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        y_test,
        predictions,
        average="binary",
        zero_division=0,
    )
    cm = confusion_matrix(y_test, predictions)

    metrics = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1_score": f1,
        "support": int(y_test.sum()),
    }
    return predictions, metrics, cm


def save_model(model, path):
    joblib.dump(model, path)


def train_and_evaluate(X_train, X_test, y_train, y_test):
    random_forest = train_classifier(X_train, y_train)
    anomaly_detector = train_anomaly_detector(X_train)
    predictions, metrics, cm = evaluate_model(random_forest, X_test, y_test)

    anomaly_scores = -anomaly_detector.score_samples(X_test)

    return {
        "random_forest": random_forest,
        "isolation_forest": anomaly_detector,
        "predictions": predictions,
        "metrics": metrics,
        "cm": cm,
        "anomaly_scores": anomaly_scores,
    }
