"""
AI-Driven Anomaly Detection System
Based on Disaster Risk Science Framework (Shi et al., 2020)

This module implements anomaly detection to identify early signs of system failure,
corresponding to the Hazard (H) and Vulnerability (V) components of the disaster system.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Isolation Forest-based anomaly detection for cloud infrastructure metrics.
    
    Detects anomalies in:
    - CPU utilization
    - Memory usage
    - Network traffic
    - Disk I/O
    - Request latency
    - Error rates
    """
    
    def __init__(self, contamination: float = 0.01, random_state: int = 42):
        """
        Initialize anomaly detector.
        
        Args:
            contamination: Expected proportion of anomalies (default: 1%)
            random_state: Random seed for reproducibility
        """
        self.contamination = contamination
        self.random_state = random_state
        self.model = IsolationForest(
            contamination=contamination,
            random_state=random_state,
            n_estimators=100,
            max_samples='auto',
            max_features=1.0,
            bootstrap=False,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
        
    def prepare_features(self, metrics: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features from raw metrics.
        
        Features include:
        - Raw metrics
        - Rolling statistics (mean, std, min, max)
        - Rate of change
        - Time-based features
        """
        features = metrics.copy()
        
        # Rolling statistics (5-minute window)
        for col in metrics.columns:
            if col != 'timestamp':
                features[f'{col}_rolling_mean'] = metrics[col].rolling(window=5, min_periods=1).mean()
                features[f'{col}_rolling_std'] = metrics[col].rolling(window=5, min_periods=1).std()
                features[f'{col}_rolling_min'] = metrics[col].rolling(window=5, min_periods=1).min()
                features[f'{col}_rolling_max'] = metrics[col].rolling(window=5, min_periods=1).max()
                
                # Rate of change
                features[f'{col}_rate_of_change'] = metrics[col].diff()
        
        # Time-based features
        if 'timestamp' in features.columns:
            features['hour'] = pd.to_datetime(features['timestamp']).dt.hour
            features['day_of_week'] = pd.to_datetime(features['timestamp']).dt.dayofweek
            features.drop('timestamp', axis=1, inplace=True)
        
        # Fill NaN values
        features.fillna(method='bfill', inplace=True)
        features.fillna(0, inplace=True)
        
        return features
    
    def train(self, historical_metrics: pd.DataFrame) -> Dict:
        """
        Train anomaly detection model on historical data.
        
        Args:
            historical_metrics: Historical metrics data
            
        Returns:
            Training statistics
        """
        logger.info("Preparing features for training...")
        features = self.prepare_features(historical_metrics)
        self.feature_names = features.columns.tolist()
        
        logger.info(f"Training on {len(features)} samples with {len(self.feature_names)} features...")
        
        # Scale features
        X_scaled = self.scaler.fit_transform(features)
        
        # Train model
        self.model.fit(X_scaled)
        self.is_trained = True
        
        # Get anomaly scores for training data
        scores = self.model.score_samples(X_scaled)
        predictions = self.model.predict(X_scaled)
        
        anomaly_count = np.sum(predictions == -1)
        anomaly_percentage = (anomaly_count / len(predictions)) * 100
        
        stats = {
            'total_samples': len(features),
            'anomalies_detected': int(anomaly_count),
            'anomaly_percentage': float(anomaly_percentage),
            'mean_score': float(np.mean(scores)),
            'std_score': float(np.std(scores)),
            'min_score': float(np.min(scores)),
            'max_score': float(np.max(scores))
        }
        
        logger.info(f"Training complete. Detected {anomaly_count} anomalies ({anomaly_percentage:.2f}%)")
        
        return stats
    
    def detect(self, current_metrics: pd.DataFrame) -> List[Dict]:
        """
        Detect anomalies in current metrics.
        
        Args:
            current_metrics: Current metrics data
            
        Returns:
            List of anomaly detections with details
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before detection")
        
        features = self.prepare_features(current_metrics)
        
        # Ensure same features as training
        for col in self.feature_names:
            if col not in features.columns:
                features[col] = 0
        features = features[self.feature_names]
        
        # Scale features
        X_scaled = self.scaler.transform(features)
        
        # Predict anomalies
        predictions = self.model.predict(X_scaled)
        scores = self.model.score_samples(X_scaled)
        
        # Prepare results
        anomalies = []
        for idx, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:  # Anomaly detected
                anomaly = {
                    'timestamp': current_metrics.iloc[idx].get('timestamp', datetime.now().isoformat()),
                    'anomaly_score': float(score),
                    'severity': self._calculate_severity(score),
                    'affected_metrics': self._identify_affected_metrics(features.iloc[idx], current_metrics.iloc[idx]),
                    'risk_level': self._assess_risk_level(score, features.iloc[idx])
                }
                anomalies.append(anomaly)
        
        return anomalies
    
    def _calculate_severity(self, score: float) -> str:
        """Calculate anomaly severity based on score."""
        if score < -0.5:
            return 'CRITICAL'
        elif score < -0.3:
            return 'HIGH'
        elif score < -0.1:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _identify_affected_metrics(self, feature_row: pd.Series, metric_row: pd.Series) -> List[str]:
        """Identify which metrics are anomalous."""
        affected = []
        
        # Check base metrics
        for col in metric_row.index:
            if col == 'timestamp':
                continue
            
            value = metric_row[col]
            
            # Simple threshold-based identification
            if col == 'cpu_utilization' and value > 80:
                affected.append(f'cpu_utilization ({value:.2f}%)')
            elif col == 'memory_usage' and value > 85:
                affected.append(f'memory_usage ({value:.2f}%)')
            elif col == 'error_rate' and value > 5:
                affected.append(f'error_rate ({value:.2f}%)')
            elif col == 'latency_ms' and value > 1000:
                affected.append(f'latency_ms ({value:.2f}ms)')
        
        return affected if affected else ['multiple_metrics']
    
    def _assess_risk_level(self, score: float, feature_row: pd.Series) -> str:
        """
        Assess disaster risk level based on Shi et al. (2020) framework.
        
        Risk = f(H, E, Ex, V, R)
        """
        # Simplified risk assessment
        hazard_score = abs(score)  # Anomaly score represents hazard
        
        if hazard_score > 0.5:
            return 'EXTREME'
        elif hazard_score > 0.3:
            return 'HIGH'
        elif hazard_score > 0.1:
            return 'MODERATE'
        else:
            return 'LOW'
    
    def save_model(self, filepath: str):
        """Save trained model to disk."""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'contamination': self.contamination,
            'random_state': self.random_state
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained model from disk."""
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.contamination = model_data['contamination']
        self.random_state = model_data['random_state']
        self.is_trained = True
        
        logger.info(f"Model loaded from {filepath}")


class RealTimeAnomalyMonitor:
    """
    Real-time anomaly monitoring system.
    
    Continuously monitors metrics and triggers alerts when anomalies are detected.
    """
    
    def __init__(self, detector: AnomalyDetector, alert_callback=None):
        """
        Initialize real-time monitor.
        
        Args:
            detector: Trained anomaly detector
            alert_callback: Function to call when anomaly detected
        """
        self.detector = detector
        self.alert_callback = alert_callback
        self.anomaly_history = []
        
    def process_metrics(self, metrics: pd.DataFrame) -> Dict:
        """
        Process incoming metrics and detect anomalies.
        
        Args:
            metrics: Current metrics data
            
        Returns:
            Processing results with anomalies
        """
        anomalies = self.detector.detect(metrics)
        
        # Store in history
        self.anomaly_history.extend(anomalies)
        
        # Trigger alerts
        if anomalies and self.alert_callback:
            for anomaly in anomalies:
                self.alert_callback(anomaly)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'metrics_processed': len(metrics),
            'anomalies_detected': len(anomalies),
            'anomalies': anomalies,
            'status': 'ALERT' if anomalies else 'NORMAL'
        }
        
        return result
    
    def get_anomaly_summary(self, hours: int = 24) -> Dict:
        """Get summary of anomalies in the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_anomalies = [
            a for a in self.anomaly_history
            if datetime.fromisoformat(a['timestamp']) > cutoff_time
        ]
        
        severity_counts = {}
        risk_counts = {}
        
        for anomaly in recent_anomalies:
            severity = anomaly['severity']
            risk = anomaly['risk_level']
            
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        return {
            'time_window_hours': hours,
            'total_anomalies': len(recent_anomalies),
            'severity_distribution': severity_counts,
            'risk_distribution': risk_counts,
            'recent_anomalies': recent_anomalies[-10:]  # Last 10
        }


def generate_sample_metrics(num_samples: int = 1000, include_anomalies: bool = True) -> pd.DataFrame:
    """
    Generate sample metrics for testing.
    
    Args:
        num_samples: Number of samples to generate
        include_anomalies: Whether to include synthetic anomalies
        
    Returns:
        DataFrame with sample metrics
    """
    np.random.seed(42)
    
    timestamps = pd.date_range(start='2024-01-01', periods=num_samples, freq='1min')
    
    # Normal patterns
    cpu = np.random.normal(50, 10, num_samples)
    memory = np.random.normal(60, 8, num_samples)
    network_in = np.random.normal(1000, 200, num_samples)
    network_out = np.random.normal(800, 150, num_samples)
    disk_io = np.random.normal(500, 100, num_samples)
    latency = np.random.normal(100, 20, num_samples)
    error_rate = np.random.normal(0.5, 0.2, num_samples)
    
    # Add anomalies
    if include_anomalies:
        anomaly_indices = np.random.choice(num_samples, size=int(num_samples * 0.02), replace=False)
        
        for idx in anomaly_indices:
            cpu[idx] = np.random.uniform(90, 100)
            memory[idx] = np.random.uniform(85, 95)
            latency[idx] = np.random.uniform(500, 2000)
            error_rate[idx] = np.random.uniform(5, 15)
    
    metrics = pd.DataFrame({
        'timestamp': timestamps,
        'cpu_utilization': np.clip(cpu, 0, 100),
        'memory_usage': np.clip(memory, 0, 100),
        'network_in_mbps': np.clip(network_in, 0, None),
        'network_out_mbps': np.clip(network_out, 0, None),
        'disk_io_ops': np.clip(disk_io, 0, None),
        'latency_ms': np.clip(latency, 0, None),
        'error_rate': np.clip(error_rate, 0, 100)
    })
    
    return metrics


if __name__ == "__main__":
    # Example usage
    logger.info("Generating sample metrics...")
    historical_data = generate_sample_metrics(num_samples=5000, include_anomalies=True)
    
    logger.info("Training anomaly detector...")
    detector = AnomalyDetector(contamination=0.02)
    stats = detector.train(historical_data)
    
    logger.info(f"Training statistics: {json.dumps(stats, indent=2)}")
    
    # Save model
    detector.save_model('anomaly_detector_model.pkl')
    
    # Test on new data
    logger.info("Testing on new metrics...")
    test_data = generate_sample_metrics(num_samples=100, include_anomalies=True)
    anomalies = detector.detect(test_data)
    
    logger.info(f"Detected {len(anomalies)} anomalies in test data")
    
    for anomaly in anomalies[:5]:  # Show first 5
        logger.info(f"Anomaly: {json.dumps(anomaly, indent=2)}")
    
    # Real-time monitoring example
    def alert_handler(anomaly):
        logger.warning(f"ALERT: {anomaly['severity']} anomaly detected - {anomaly['affected_metrics']}")
    
    monitor = RealTimeAnomalyMonitor(detector, alert_callback=alert_handler)
    
    # Process metrics in batches
    for i in range(0, len(test_data), 10):
        batch = test_data.iloc[i:i+10]
        result = monitor.process_metrics(batch)
        
        if result['status'] == 'ALERT':
            logger.info(f"Batch {i//10}: {result['anomalies_detected']} anomalies detected")
    
    # Get summary
    summary = monitor.get_anomaly_summary(hours=1)
    logger.info(f"Anomaly summary: {json.dumps(summary, indent=2)}")
