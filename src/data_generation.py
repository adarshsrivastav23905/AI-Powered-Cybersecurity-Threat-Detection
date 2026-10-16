from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def generate_synthetic_dataset(output_path: str | Path = "data/cyber_threat_dataset.csv", rows: int = 5000) -> pd.DataFrame:
    """Create a realistic synthetic cybersecurity dataset for training and portfolio use."""
    rng = np.random.default_rng(42)
    records = []

    protocols = ["TCP", "UDP", "ICMP", "HTTP", "HTTPS"]
    attack_types = ["DoS", "BruteForce", "PortScan", "Malware"]
    source_ips = [f"10.0.0.{i}" for i in range(1, 101)]
    dest_ips = [f"192.168.1.{i}" for i in range(1, 51)]

    for _ in range(rows):
        is_attack = rng.random() < 0.22

        if is_attack:
            attack_type = rng.choice(attack_types)
            connection_duration = round(rng.uniform(15.0, 300.0), 2)
            bytes_sent = int(rng.normal(25000, 18000))
            bytes_received = int(rng.normal(32000, 22000))
            failed_logins = int(rng.integers(3, 25))
            request_frequency = int(rng.integers(50, 350))
            protocol = rng.choice(protocols)
            packet_size = int(rng.normal(1500, 500))
            ports_touched = int(rng.integers(3, 20))
            blocked = int(rng.choice([0, 1], p=[0.2, 0.8]))
            severity = "High" if attack_type in {"DoS", "Malware"} else "Medium"
            label = "Attack"
        else:
            attack_type = "Normal"
            connection_duration = round(rng.uniform(0.1, 25.0), 2)
            bytes_sent = int(rng.normal(900, 500))
            bytes_received = int(rng.normal(1200, 700))
            failed_logins = int(rng.integers(0, 3))
            request_frequency = int(rng.integers(2, 50))
            protocol = rng.choice(protocols)
            packet_size = int(rng.normal(700, 150))
            ports_touched = int(rng.integers(1, 4))
            blocked = 0
            severity = "Low"
            label = "Normal"

        record = {
            "timestamp": pd.Timestamp("2024-01-01") + pd.to_timedelta(rng.integers(0, 86400, size=1)[0], unit="s"),
            "source_ip": rng.choice(source_ips),
            "destination_ip": rng.choice(dest_ips),
            "protocol": protocol,
            "connection_duration_seconds": connection_duration,
            "bytes_sent": max(bytes_sent, 10),
            "bytes_received": max(bytes_received, 10),
            "failed_logins": failed_logins,
            "request_frequency_per_min": request_frequency,
            "packet_size_bytes": max(packet_size, 100),
            "ports_touched": ports_touched,
            "blocked": blocked,
            "attack_type": attack_type,
            "severity": severity,
            "label": label,
        }
        records.append(record)

    df = pd.DataFrame(records)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Synthetic cybersecurity dataset created at: {output_path.resolve()}")
    return df


if __name__ == "__main__":
    generate_synthetic_dataset()
