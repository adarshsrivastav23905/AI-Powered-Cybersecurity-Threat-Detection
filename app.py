from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.model_selection import train_test_split

from src.modeling import train_and_evaluate
from src.preprocessing import load_dataset, prepare_features_for_training


PROJECT_DIR = Path(__file__).resolve().parent
DATA_PATH = PROJECT_DIR / "data" / "cyber_threat_dataset.csv"

st.set_page_config(
    page_title="Cyber Signal | Threat detection",
    page_icon=":material/security:",
    layout="wide",
)

st.html(
    """
    <style>
    :root {
        --signal-ink: #e8eef8;
        --signal-muted: #91a1b8;
        --signal-line: rgba(151, 174, 204, 0.14);
        --signal-teal: #46e0bd;
        --signal-blue: #76a9ff;
    }

    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(ellipse at 78% 0%, rgba(28, 77, 112, 0.20), transparent 34rem),
            #080f1b;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0c1625 0%, #0a1220 100%);
        border-right: 1px solid var(--signal-line);
    }

    .block-container {
        max-width: 1540px;
        padding-top: 2.25rem;
        padding-bottom: 3rem;
    }

    .signal-hero {
        position: relative;
        overflow: hidden;
        padding: 2rem 2.25rem;
        border: 1px solid rgba(117, 157, 202, 0.20);
        border-radius: 22px;
        background:
            radial-gradient(ellipse at 88% 14%, rgba(70, 224, 189, 0.13), transparent 24rem),
            linear-gradient(120deg, rgba(18, 34, 54, 0.98), rgba(12, 24, 40, 0.93));
        box-shadow: 0 18px 60px rgba(0, 0, 0, 0.16);
        margin: 0.25rem 0 1.35rem;
    }

    .signal-hero::after {
        content: "";
        position: absolute;
        width: 210px;
        height: 210px;
        right: 5%;
        top: -145px;
        border: 1px solid rgba(70, 224, 189, 0.18);
        border-radius: 50%;
        box-shadow: 0 0 0 26px rgba(70, 224, 189, 0.025),
                    0 0 0 54px rgba(70, 224, 189, 0.02);
        pointer-events: none;
    }

    .signal-eyebrow {
        color: var(--signal-teal);
        font: 700 0.70rem/1.2 ui-monospace, SFMono-Regular, Consolas, monospace;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-bottom: 0.75rem;
    }

    .signal-title {
        color: var(--signal-ink);
        font-size: clamp(1.8rem, 3vw, 2.55rem);
        font-weight: 700;
        letter-spacing: -0.045em;
        line-height: 1.12;
        margin: 0;
    }

    .signal-description {
        max-width: 720px;
        color: #a9b8ca;
        font-size: 0.98rem;
        line-height: 1.65;
        margin: 0.8rem 0 0;
    }

    .signal-status {
        position: absolute;
        right: 1.65rem;
        bottom: 1.55rem;
        display: inline-flex;
        align-items: center;
        gap: 0.55rem;
        padding: 0.52rem 0.8rem;
        border: 1px solid rgba(70, 224, 189, 0.24);
        border-radius: 999px;
        background: rgba(70, 224, 189, 0.07);
        color: #a7f4df;
        font: 650 0.68rem/1 ui-monospace, SFMono-Regular, Consolas, monospace;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }

    .signal-status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: var(--signal-teal);
        box-shadow: 0 0 12px rgba(70, 224, 189, 0.75);
    }

    [data-testid="stMetric"] {
        min-height: 112px;
        padding: 1rem 1.1rem;
        border: 1px solid var(--signal-line);
        border-radius: 16px;
        background: linear-gradient(145deg, rgba(19, 32, 50, 0.92), rgba(12, 23, 38, 0.92));
        box-shadow: 0 8px 26px rgba(0, 0, 0, 0.10);
    }

    [data-testid="stMetricLabel"] {
        color: var(--signal-muted);
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.025em;
    }

    [data-testid="stMetricValue"] {
        color: var(--signal-ink);
        font-weight: 700;
        letter-spacing: -0.035em;
    }

    [data-testid="stVerticalBlockBorderWrapper"] {
        border-color: var(--signal-line);
        border-radius: 17px;
        background: linear-gradient(155deg, rgba(16, 29, 47, 0.78), rgba(11, 21, 35, 0.68));
    }

    [data-testid="stTabs"] [role="tab"] {
        min-height: 2.75rem;
        padding: 0.5rem 1rem;
        border-radius: 10px 10px 0 0;
        color: var(--signal-muted);
        font-weight: 600;
    }

    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        color: var(--signal-teal);
    }

    [data-testid="stDataFrame"] {
        border: 1px solid var(--signal-line);
        border-radius: 12px;
        overflow: hidden;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.85rem;
    }

    [data-testid="stSidebar"] h3 {
        letter-spacing: -0.02em;
    }

    [data-testid="stCaptionContainer"] {
        color: var(--signal-muted);
    }

    @media (max-width: 700px) {
        .block-container {
            padding-top: 1.25rem;
        }

        .signal-hero {
            padding: 1.45rem 1.25rem 4.1rem;
            border-radius: 17px;
        }

        .signal-status {
            right: auto;
            left: 1.25rem;
            bottom: 1.2rem;
        }
    }
    </style>
    """
)


@st.cache_resource(show_spinner=False)
def load_analysis(data_path: str, modified_time: float):
    raw_data = load_dataset(data_path)
    features, labels, _, _ = prepare_features_for_training(raw_data)

    X_train, X_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.25,
        random_state=42,
        stratify=labels,
    )
    model_bundle = train_and_evaluate(X_train, X_test, y_train, y_test)

    test_events = raw_data.loc[X_test.index].copy()
    test_events["predicted_label"] = model_bundle["predictions"]
    test_events["threat_probability"] = model_bundle["random_forest"].predict_proba(X_test)[:, 1]
    test_events["anomaly_score"] = model_bundle["anomaly_scores"]
    test_events["is_alert"] = (
        (test_events["predicted_label"] == 1)
        | (test_events["anomaly_score"] > 0.65)
    )
    test_events["alert_severity"] = np.select(
        [
            (test_events["threat_probability"] >= 0.8)
            | (test_events["anomaly_score"] > 1.0),
            test_events["threat_probability"] >= 0.6,
        ],
        ["Critical", "High"],
        default="Medium",
    )

    return raw_data, test_events, model_bundle


st.html(
    """
    <section class="signal-hero" aria-label="Cyber Signal dashboard">
      <div class="signal-eyebrow">Cyber Signal <span aria-hidden="true">/</span> Security analytics</div>
      <h1 class="signal-title">Threat detection console</h1>
      <p class="signal-description">
        A focused view of simulated network activity, model detections, and investigation signals.
        Built for exploration—not connected to live infrastructure.
      </p>
      <div class="signal-status"><span class="signal-status-dot"></span>Local simulation</div>
    </section>
    """
)

if not DATA_PATH.exists():
    st.error(f"Dataset not found: {DATA_PATH}. Run `python main.py --generate-data` first.")
    st.stop()

with st.sidebar:
    st.markdown("### :material/security: Cyber Signal")
    st.caption("THREAT DETECTION WORKSPACE")
    st.markdown("#### Detection controls")
    st.caption("Tune the events shown in your investigation views.")

    if st.button("Retrain models", icon=":material/refresh:", width="stretch"):
        load_analysis.clear()

    attack_types = st.multiselect(
        "Attack category",
        options=["DoS", "BruteForce", "PortScan", "Malware", "Normal"],
        default=["DoS", "BruteForce", "PortScan", "Malware", "Normal"],
    )
    severities = st.multiselect(
        "Alert severity",
        options=["Critical", "High", "Medium"],
        default=["Critical", "High", "Medium"],
    )
    alerts_only = st.toggle("Show flagged events only", value=True)
    st.space("small")
    st.badge("Synthetic data", icon=":material/science:", color="blue")
    st.caption("No live network data is collected.")

with st.spinner("Analyzing traffic and training detection models..."):
    raw_data, test_events, model_bundle = load_analysis(
        str(DATA_PATH),
        DATA_PATH.stat().st_mtime,
    )

metrics = model_bundle["metrics"]
flagged = test_events[test_events["is_alert"]]

with st.container(horizontal=True):
    st.metric("Events in dataset", f"{len(raw_data):,}", border=True)
    st.metric("Flagged in test set", f"{len(flagged):,}", border=True)
    st.metric("Detection precision", f"{metrics['precision']:.1%}", border=True)
    st.metric("Attack recall", f"{metrics['recall']:.1%}", border=True)
    st.metric("F1 score", f"{metrics['f1_score']:.1%}", border=True)

st.caption(
    f"Model evaluation uses a held-out sample of {len(test_events):,} events. "
    "Synthetic-data scores are illustrative and should not be interpreted as production performance."
)

overview_tab, alerts_tab, traffic_tab, model_tab = st.tabs(
    ["Overview", "Alert queue", "Traffic data", "Model performance"]
)

with overview_tab:
    chart_col, trend_col = st.columns(2)

    with chart_col:
        with st.container(border=True):
            st.subheader("Traffic by category")
            category_counts = (
                raw_data["attack_type"]
                .value_counts()
                .rename_axis("Attack type")
                .reset_index(name="Events")
            )
            st.bar_chart(category_counts, x="Attack type", y="Events")

    with trend_col:
        with st.container(border=True):
            st.subheader("Flagged activity over time")
            hourly_alerts = flagged.assign(
                hour=pd.to_datetime(flagged["timestamp"]).dt.floor("h")
            ).groupby("hour").size().rename("Flagged events").reset_index()
            if hourly_alerts.empty:
                st.info("No flagged events in the current test sample.")
            else:
                st.line_chart(hourly_alerts, x="hour", y="Flagged events")

    with st.container(border=True):
        st.subheader("Latest high-confidence alerts")
        latest_alerts = flagged.sort_values(
            ["threat_probability", "timestamp"],
            ascending=[False, False],
        )
        alert_columns = [
            "timestamp",
            "source_ip",
            "destination_ip",
            "attack_type",
            "alert_severity",
            "threat_probability",
        ]
        st.dataframe(
            latest_alerts[alert_columns].head(8),
            hide_index=True,
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Time", format="MMM D, HH:mm:ss"),
                "source_ip": st.column_config.TextColumn("Source"),
                "destination_ip": st.column_config.TextColumn("Destination"),
                "attack_type": st.column_config.TextColumn("Category"),
                "alert_severity": st.column_config.TextColumn("Alert severity"),
                "threat_probability": st.column_config.ProgressColumn(
                    "Threat confidence",
                    min_value=0,
                    max_value=1,
                    format="percent",
                ),
            },
        )

with alerts_tab:
    st.subheader("Alert queue")
    st.caption("Alerts are generated from model predictions or elevated anomaly scores.")
    filtered_alerts = test_events[
        test_events["attack_type"].isin(attack_types)
        & test_events["alert_severity"].isin(severities)
    ].copy()
    if alerts_only:
        filtered_alerts = filtered_alerts[filtered_alerts["is_alert"]]
    filtered_alerts = filtered_alerts.sort_values(
        ["threat_probability", "timestamp"],
        ascending=[False, False],
    )

    st.metric("Events matching current filters", f"{len(filtered_alerts):,}")
    if filtered_alerts.empty:
        st.info("No events match these filters. Try selecting more categories or severities.")
    else:
        st.dataframe(
            filtered_alerts[
                [
                    "timestamp",
                    "source_ip",
                    "destination_ip",
                    "protocol",
                    "attack_type",
                    "alert_severity",
                    "threat_probability",
                    "anomaly_score",
                    "label",
                ]
            ],
            hide_index=True,
            column_config={
                "timestamp": st.column_config.DatetimeColumn("Time", format="MMM D, HH:mm:ss"),
                "source_ip": st.column_config.TextColumn("Source"),
                "destination_ip": st.column_config.TextColumn("Destination"),
                "protocol": st.column_config.TextColumn("Protocol"),
                "attack_type": st.column_config.TextColumn("Category"),
                "alert_severity": st.column_config.TextColumn("Alert severity"),
                "threat_probability": st.column_config.ProgressColumn(
                    "Threat confidence",
                    min_value=0,
                    max_value=1,
                    format="percent",
                ),
                "anomaly_score": st.column_config.NumberColumn("Anomaly score", format="%.3f"),
                "label": st.column_config.TextColumn("Dataset label"),
            },
        )

with traffic_tab:
    st.subheader("Simulated network events")
    st.caption("The table contains generated, private-range IP addresses—not captured network traffic.")
    traffic_filter = raw_data[raw_data["attack_type"].isin(attack_types)]
    st.dataframe(
        traffic_filter[
            [
                "timestamp",
                "source_ip",
                "destination_ip",
                "protocol",
                "connection_duration_seconds",
                "bytes_sent",
                "bytes_received",
                "failed_logins",
                "request_frequency_per_min",
                "attack_type",
                "severity",
                "label",
            ]
        ].sort_values("timestamp", ascending=False),
        hide_index=True,
        column_config={
            "timestamp": st.column_config.DatetimeColumn("Time", format="MMM D, HH:mm:ss"),
            "source_ip": st.column_config.TextColumn("Source"),
            "destination_ip": st.column_config.TextColumn("Destination"),
            "connection_duration_seconds": st.column_config.NumberColumn("Duration (sec)", format="%.2f"),
            "bytes_sent": st.column_config.NumberColumn("Bytes sent", format="%d"),
            "bytes_received": st.column_config.NumberColumn("Bytes received", format="%d"),
            "failed_logins": st.column_config.NumberColumn("Failed logins", format="%d"),
            "request_frequency_per_min": st.column_config.NumberColumn("Requests/min", format="%d"),
            "attack_type": st.column_config.TextColumn("Category"),
            "severity": st.column_config.TextColumn("Dataset severity"),
            "label": st.column_config.TextColumn("Label"),
        },
    )

with model_tab:
    metrics_col, matrix_col = st.columns(2)
    with metrics_col:
        with st.container(border=True):
            st.subheader("Held-out evaluation")
            st.dataframe(
                pd.DataFrame(
                    {
                        "Metric": ["Accuracy", "Precision", "Recall", "F1 score"],
                        "Score": [
                            metrics["accuracy"],
                            metrics["precision"],
                            metrics["recall"],
                            metrics["f1_score"],
                        ],
                    }
                ),
                hide_index=True,
                column_config={"Score": st.column_config.NumberColumn(format="percent")},
            )
            st.caption(f"Test events: {len(test_events):,} · Random Forest classifier")

    with matrix_col:
        with st.container(border=True):
            st.subheader("Confusion matrix")
            confusion = pd.DataFrame(
                model_bundle["cm"],
                index=["Actual normal", "Actual attack"],
                columns=["Predicted normal", "Predicted attack"],
            )
            st.dataframe(confusion, width="stretch")

    importance_col, anomaly_col = st.columns(2)
    with importance_col:
        with st.container(border=True):
            st.subheader("Top model signals")
            importance = (
                pd.DataFrame(
                    {
                        "Feature": model_bundle["random_forest"].feature_names_in_,
                        "Importance": model_bundle["random_forest"].feature_importances_,
                    }
                )
                .sort_values("Importance", ascending=False)
                .head(10)
                .sort_values("Importance")
            )
            importance["Feature"] = importance["Feature"].replace(
                {
                    "connection_duration_seconds": "Duration (sec)",
                    "packet_size_bytes": "Packet size",
                    "request_frequency_per_min": "Requests/min",
                    "protocol_HTTP": "HTTP protocol",
                    "protocol_TCP": "TCP protocol",
                }
            )
            st.bar_chart(
                importance.set_index("Feature"),
                y="Importance",
                horizontal=True,
            )

    with anomaly_col:
        with st.container(border=True):
            st.subheader("Anomaly score distribution")
            anomaly_histogram = (
                pd.cut(test_events["anomaly_score"], bins=20)
                .value_counts(sort=False)
                .rename_axis("Score range")
                .reset_index(name="Events")
            )
            anomaly_histogram["Score range"] = anomaly_histogram["Score range"].astype(str)
            st.bar_chart(anomaly_histogram, x="Score range", y="Events")

st.caption("AI-powered cybersecurity threat detection · Educational simulation only")
