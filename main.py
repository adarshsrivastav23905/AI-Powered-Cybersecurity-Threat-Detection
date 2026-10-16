from pathlib import Path
import argparse

from src.data_generation import generate_synthetic_dataset
from src.preprocessing import load_and_prepare_data
from src.modeling import train_and_evaluate
from src.visualization import save_visualizations
from src.alerting import build_alert_summary


def parse_args():
    parser = argparse.ArgumentParser(description="AI-powered cybersecurity threat detection pipeline")
    parser.add_argument("--data-path", type=str, default="data/cyber_threat_dataset.csv", help="Path to the dataset CSV")
    parser.add_argument("--generate-data", action="store_true", help="Generate a new synthetic dataset before training")
    parser.add_argument("--output-dir", type=str, default="outputs", help="Directory to save generated output files")
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    data_path = Path(args.data_path)
    if args.generate_data:
        generate_synthetic_dataset(output_path=data_path)

    X_train, X_test, y_train, y_test, feature_names, df = load_and_prepare_data(data_path)
    model_bundle = train_and_evaluate(X_train, X_test, y_train, y_test)
    alerts = build_alert_summary(model_bundle["random_forest"], X_test, y_test, model_bundle["isolation_forest"], df)

    print("\n=== Model evaluation summary ===")
    print(f"Accuracy: {model_bundle['metrics']['accuracy']:.4f}")
    print(f"Precision: {model_bundle['metrics']['precision']:.4f}")
    print(f"Recall: {model_bundle['metrics']['recall']:.4f}")
    print(f"F1 score: {model_bundle['metrics']['f1_score']:.4f}")
    print(f"Support: {model_bundle['metrics']['support']}\n")

    print("Top 5 alerts:")
    print(alerts.head().to_string(index=False))

    save_visualizations(
        model_bundle["random_forest"],
        feature_names,
        model_bundle["cm"],
        model_bundle["anomaly_scores"],
        output_dir,
    )

    print(f"\nOutputs saved to: {output_dir.resolve()}")
    print(f"Dataset used: {data_path.resolve()}")


if __name__ == "__main__":
    main()
