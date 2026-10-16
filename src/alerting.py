from __future__ import annotations

import pandas as pd


def build_alert_summary(model, X_test, y_test, anomaly_model, full_dataset):
    probabilities = model.predict_proba(X_test)[:, 1]
    anomaly_scores = -anomaly_model.score_samples(X_test)

    test_df = X_test.copy()
    test_df["actual_label"] = y_test.to_numpy()
    test_df["predicted_label"] = model.predict(X_test)
    test_df["probability"] = probabilities
    test_df["anomaly_score"] = anomaly_scores

    alert_rows = []
    for _, row in test_df.iterrows():
        if row["predicted_label"] == 1 or row["anomaly_score"] > 0.65:
            if row["probability"] >= 0.8 or row["anomaly_score"] > 1.0:
                level = "Critical"
            elif row["probability"] >= 0.6:
                level = "High"
            else:
                level = "Medium"

            alert_rows.append(
                {
                    "actual_label": row["actual_label"],
                    "predicted_label": row["predicted_label"],
                    "probability": round(float(row["probability"]), 4),
                    "anomaly_score": round(float(row["anomaly_score"]), 4),
                    "severity": level,
                }
            )

    if not alert_rows:
        return pd.DataFrame(columns=["actual_label", "predicted_label", "probability", "anomaly_score", "severity"])

    alert_df = pd.DataFrame(alert_rows)
    return alert_df.sort_values(by=["severity", "probability"], ascending=[False, False]).head(10)
