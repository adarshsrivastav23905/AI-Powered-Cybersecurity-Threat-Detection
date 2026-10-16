from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


def save_confusion_matrix(cm, output_dir: str | Path):
    output_path = Path(output_dir) / "confusion_matrix.png"
    plt.figure(figsize=(7, 5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.xlabel("Predicted label")
    plt.ylabel("Actual label")
    plt.title("Cybersecurity Threat Confusion Matrix")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path


def save_feature_importance(model, feature_names, output_dir: str | Path):
    output_path = Path(output_dir) / "feature_importance.png"
    importances = model.feature_importances_
    ranked = sorted(zip(feature_names, importances), key=lambda item: item[1], reverse=True)[:10]
    labels = [item[0] for item in ranked]
    values = [item[1] for item in ranked]

    plt.figure(figsize=(8, 6))
    plt.barh(labels[::-1], values[::-1], color="steelblue")
    plt.xlabel("Importance")
    plt.title("Top 10 Features by Importance")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path


def save_anomaly_distribution(scores, output_dir: str | Path):
    output_path = Path(output_dir) / "anomaly_distribution.png"
    plt.figure(figsize=(8, 5))
    plt.hist(scores, bins=25, color="tomato", edgecolor="black")
    plt.xlabel("Anomaly score")
    plt.ylabel("Frequency")
    plt.title("Anomaly Detection Distribution")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    return output_path


def save_visualizations(model, feature_names, confusion_matrix, anomaly_scores, output_dir: str | Path):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    save_confusion_matrix(confusion_matrix, output_dir)
    save_feature_importance(model, feature_names, output_dir)
    save_anomaly_distribution(anomaly_scores, output_dir)

    print(f"Saved visual outputs to: {output_dir.resolve()}")
