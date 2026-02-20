"""
AI-Driven Anomaly Detection System
Based on Disaster Risk Science Framework (Shi et al., 2020)

Detects anomalies in cloud infrastructure metrics using Isolation Forest.
Runs standalone — no external services required.
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Isolation Forest-based anomaly detector for cloud infrastructure metrics.
    Detects: CPU spikes, memory pressure, latency anomalies, error rate surges.
    """

    def __init__(self, contamination: float = 0.01, random_state: int = 42):
        self.contamination  = contamination
        self.random_state   = random_state
        self.model          = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100,
            max_samples="auto",
            max_features=1.0,
            bootstrap=False,
            n_jobs=-1,
        )
        self.scaler       = StandardScaler()
        self.feature_names: List[str] = []
        self.is_trained   = False

    # ── Feature Engineering ────────────────────────────────────────────────────
    def prepare_features(self, metrics: pd.DataFrame) -> pd.DataFrame:
        """Build rolling stats + rate-of-change features from raw metrics."""
        features = metrics.copy()
        num_cols = [c for c in metrics.columns if c != "timestamp"]

        for col in num_cols:
            features[f"{col}_rolling_mean"] = (
                metrics[col].rolling(window=5, min_periods=1).mean()
            )
            features[f"{col}_rolling_std"] = (
                metrics[col].rolling(window=5, min_periods=1).std().fillna(0)
            )
            features[f"{col}_rolling_min"] = (
                metrics[col].rolling(window=5, min_periods=1).min()
            )
            features[f"{col}_rolling_max"] = (
                metrics[col].rolling(window=5, min_periods=1).max()
            )
            features[f"{col}_rate_of_change"] = metrics[col].diff().fillna(0)

        if "timestamp" in features.columns:
            ts = pd.to_datetime(features["timestamp"])
            features["hour"]        = ts.dt.hour
            features["day_of_week"] = ts.dt.dayofweek
            features.drop("timestamp", axis=1, inplace=True)

        features = features.bfill().fillna(0)
        features = features.replace([np.inf, -np.inf], 0)
        return features

    # ── Training ───────────────────────────────────────────────────────────────
    def train(self, historical_metrics: pd.DataFrame) -> Dict:
        logger.info("Preparing features for training...")
        features = self.prepare_features(historical_metrics)
        self.feature_names = features.columns.tolist()
        logger.info("Training on %d samples with %d features...",
                    len(features), len(self.feature_names))

        X_scaled    = self.scaler.fit_transform(features)
        self.model.fit(X_scaled)
        self.is_trained = True

        scores      = self.model.score_samples(X_scaled)
        predictions = self.model.predict(X_scaled)
        anomaly_cnt = int(np.sum(predictions == -1))
        anomaly_pct = float(anomaly_cnt / len(predictions) * 100)

        stats = {
            "total_samples":      len(features),
            "anomalies_detected": anomaly_cnt,
            "anomaly_percentage": round(anomaly_pct, 2),
            "mean_score":         float(np.mean(scores)),
            "std_score":          float(np.std(scores)),
            "min_score":          float(np.min(scores)),
            "max_score":          float(np.max(scores)),
        }
        logger.info("Training complete: %d anomalies (%.2f%%)",
                    anomaly_cnt, anomaly_pct)
        return stats

    # ── Detection ──────────────────────────────────────────────────────────────
    def detect(self, current_metrics: pd.DataFrame) -> List[Dict]:
        if not self.is_trained:
            raise RuntimeError("Model must be trained before calling detect()")

        features = self.prepare_features(current_metrics)
        for col in self.feature_names:
            if col not in features.columns:
                features[col] = 0
        features    = features[self.feature_names]
        X_scaled    = self.scaler.transform(features)
        predictions = self.model.predict(X_scaled)
        scores      = self.model.score_samples(X_scaled)

        anomalies = []
        for idx, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:
                row = current_metrics.iloc[idx]
                ts  = row.get("timestamp", datetime.now())
                ts_str = ts.isoformat() if hasattr(ts, "isoformat") else str(ts)
                anomalies.append({
                    "timestamp":       ts_str,
                    "anomaly_score":   float(score),
                    "severity":        self._severity(score),
                    "affected_metrics": self._affected(row),
                    "risk_level":      self._risk(score),
                })
        return anomalies

    # ── Helpers ────────────────────────────────────────────────────────────────
    def _severity(self, score: float) -> str:
        if score < -0.5:  return "CRITICAL"
        if score < -0.3:  return "HIGH"
        if score < -0.1:  return "MEDIUM"
        return "LOW"

    def _risk(self, score: float) -> str:
        h = abs(score)
        if h > 0.5:  return "EXTREME"
        if h > 0.3:  return "HIGH"
        if h > 0.1:  return "MODERATE"
        return "LOW"

    def _affected(self, row: pd.Series) -> List[str]:
        affected = []
        checks = [
            ("cpu_utilization", 80,   lambda v: f"cpu_utilization ({v:.1f}%)"),
            ("memory_usage",    85,   lambda v: f"memory_usage ({v:.1f}%)"),
            ("error_rate",       5,   lambda v: f"error_rate ({v:.2f}%)"),
            ("latency_ms",    1000,   lambda v: f"latency_ms ({v:.0f}ms)"),
        ]
        for col, threshold, fmt in checks:
            if col in row.index and row[col] > threshold:
                affected.append(fmt(row[col]))
        return affected or ["multiple_metrics"]

    # ── Persistence ────────────────────────────────────────────────────────────
    def save_model(self, filepath: str):
        if not self.is_trained:
            raise RuntimeError("Cannot save untrained model")
        joblib.dump({
            "model":         self.model,
            "scaler":        self.scaler,
            "feature_names": self.feature_names,
            "contamination": self.contamination,
            "random_state":  self.random_state,
        }, filepath)
        logger.info("Model saved to %s", filepath)

    def load_model(self, filepath: str):
        data = joblib.load(filepath)
        self.model          = data["model"]
        self.scaler         = data["scaler"]
        self.feature_names  = data["feature_names"]
        self.contamination  = data["contamination"]
        self.random_state   = data["random_state"]
        self.is_trained     = True
        logger.info("Model loaded from %s", filepath)


# ── Real-time monitor ──────────────────────────────────────────────────────────
class RealTimeAnomalyMonitor:
    """Wraps AnomalyDetector for streaming / batch use."""

    def __init__(self, detector: AnomalyDetector, alert_callback=None):
        self.detector        = detector
        self.alert_callback  = alert_callback
        self.anomaly_history: List[Dict] = []

    def process_metrics(self, metrics: pd.DataFrame) -> Dict:
        anomalies = self.detector.detect(metrics)
        self.anomaly_history.extend(anomalies)
        if anomalies and self.alert_callback:
            for a in anomalies:
                self.alert_callback(a)
        return {
            "timestamp":         datetime.now().isoformat(),
            "metrics_processed": len(metrics),
            "anomalies_detected": len(anomalies),
            "anomalies":         anomalies,
            "status":            "ALERT" if anomalies else "NORMAL",
        }

    def get_anomaly_summary(self, hours: int = 24) -> Dict:
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [
            a for a in self.anomaly_history
            if datetime.fromisoformat(a["timestamp"]) > cutoff
        ]
        sev_counts  = {}
        risk_counts = {}
        for a in recent:
            sev_counts[a["severity"]]     = sev_counts.get(a["severity"], 0)  + 1
            risk_counts[a["risk_level"]]  = risk_counts.get(a["risk_level"], 0) + 1
        return {
            "time_window_hours":    hours,
            "total_anomalies":      len(recent),
            "severity_distribution": sev_counts,
            "risk_distribution":    risk_counts,
            "recent_anomalies":     recent[-10:],
        }


# ── Sample data generator ──────────────────────────────────────────────────────
def generate_sample_metrics(num_samples: int = 1000,
                             include_anomalies: bool = True) -> pd.DataFrame:
    np.random.seed(42)
    timestamps  = pd.date_range(start="2024-01-01",
                                periods=num_samples, freq="1min")
    cpu         = np.random.normal(50, 10, num_samples)
    memory      = np.random.normal(60,  8, num_samples)
    network_in  = np.random.normal(1000, 200, num_samples)
    network_out = np.random.normal(800,  150, num_samples)
    disk_io     = np.random.normal(500,  100, num_samples)
    latency     = np.random.normal(100,   20, num_samples)
    error_rate  = np.random.normal(0.5,  0.2, num_samples)

    if include_anomalies:
        for idx in np.random.choice(num_samples,
                                    size=int(num_samples * 0.02),
                                    replace=False):
            cpu[idx]        = np.random.uniform(90, 100)
            memory[idx]     = np.random.uniform(85, 95)
            latency[idx]    = np.random.uniform(500, 2000)
            error_rate[idx] = np.random.uniform(5, 15)

    return pd.DataFrame({
        "timestamp":         timestamps,
        "cpu_utilization":   np.clip(cpu,         0, 100),
        "memory_usage":      np.clip(memory,       0, 100),
        "network_in_mbps":   np.clip(network_in,   0, None),
        "network_out_mbps":  np.clip(network_out,  0, None),
        "disk_io_ops":       np.clip(disk_io,      0, None),
        "latency_ms":        np.clip(latency,      0, None),
        "error_rate":        np.clip(error_rate,   0, 100),
    })


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("=== Anomaly Detection Model Starting ===")

    # Train
    logger.info("Generating training data (5 000 samples)...")
    hist = generate_sample_metrics(num_samples=5000, include_anomalies=True)
    detector = AnomalyDetector(contamination=0.02)
    stats    = detector.train(hist)
    logger.info("Training stats: %s", json.dumps(stats, indent=2))

    # Save model
    detector.save_model("anomaly_detector_model.pkl")

    # Test
    logger.info("Running detection on 100 fresh samples...")
    test   = generate_sample_metrics(num_samples=100, include_anomalies=True)
    result = detector.detect(test)
    logger.info("Detected %d anomalies", len(result))

    # Real-time simulation
    def alert_handler(a):
        logger.warning("ALERT [%s]: %s — affected: %s",
                       a["severity"], a["risk_level"], a["affected_metrics"])

    monitor = RealTimeAnomalyMonitor(detector, alert_callback=alert_handler)
    for i in range(0, len(test), 10):
        batch  = test.iloc[i:i + 10]
        out    = monitor.process_metrics(batch)
        if out["status"] == "ALERT":
            logger.info("Batch %d: %d anomaly/ies found",
                        i // 10, out["anomalies_detected"])

    summary = monitor.get_anomaly_summary(hours=1)
    logger.info("Summary: %s", json.dumps(summary, indent=2))
    logger.info("=== Anomaly Detection Model Ready ===")
