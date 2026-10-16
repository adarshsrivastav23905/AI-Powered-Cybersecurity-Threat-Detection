from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split


def load_dataset(path: str | Path) -> pd.DataFrame:
    dataset = pd.read_csv(path)
    return dataset


def prepare_features_for_training(dataset: pd.DataFrame):
    df = dataset.copy()

    if "timestamp" in df.columns:
        df = df.drop(columns=["timestamp"])

    if "source_ip" in df.columns:
        df = df.drop(columns=["source_ip"])

    if "destination_ip" in df.columns:
        df = df.drop(columns=["destination_ip"])

    df = df.fillna(df.median(numeric_only=True))
    for column in df.select_dtypes(include=["object", "category"]).columns:
        df[column] = df[column].fillna(df[column].mode()[0])

    feature_columns = [column for column in df.columns if column not in {"label", "attack_type", "severity"}]
    X = pd.get_dummies(df[feature_columns], drop_first=False)
    y = df["label"].map({"Normal": 0, "Attack": 1})

    return X, y, feature_columns, df


def load_and_prepare_data(path: str | Path):
    dataset = load_dataset(path)
    X, y, feature_names, df = prepare_features_for_training(dataset)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    return X_train, X_test, y_train, y_test, feature_names, df
