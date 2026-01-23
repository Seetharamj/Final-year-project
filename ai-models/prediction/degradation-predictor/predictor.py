"""
Service Degradation Prediction System
Based on Disaster Risk Science Framework (Shi et al., 2020)

This module implements predictive models to forecast service degradation,
enabling proactive disaster prevention (Disaster Science pillar).
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceDegradationPredictor:
    """
    Predicts service degradation using ensemble machine learning models.
    
    Predicts:
    - Time to failure (regression)
    - Degradation probability (classification)
    - Severity level (multi-class classification)
    """
    
    def __init__(self, prediction_horizon_minutes: int = 15):
        """
        Initialize predictor.
        
        Args:
            prediction_horizon_minutes: How far ahead to predict (default: 15 minutes)
        """
        self.prediction_horizon = prediction_horizon_minutes
        
        # Time to failure predictor (regression)
        self.ttf_model = RandomForestRegressor(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1
        )
        
        # Degradation probability predictor (binary classification)
        self.degradation_model = GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        # Severity predictor (multi-class)
        self.severity_model = GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        self.scaler = StandardScaler()
        self.feature_names = []
        self.is_trained = False
        
    def prepare_features(self, metrics: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare features for prediction.
        
        Features include:
        - Current metrics
        - Trend indicators
        - Statistical aggregations
        - Time-based features
        """
        features = metrics.copy()
        
        # Trend features (last 5, 10, 15 minutes)
        for window in [5, 10, 15]:
            for col in metrics.columns:
                if col not in ['timestamp', 'degraded', 'time_to_failure', 'severity']:
                    # Moving average
                    features[f'{col}_ma_{window}'] = metrics[col].rolling(window=window, min_periods=1).mean()
                    
                    # Trend (slope)
                    features[f'{col}_trend_{window}'] = metrics[col].rolling(window=window, min_periods=1).apply(
                        lambda x: np.polyfit(range(len(x)), x, 1)[0] if len(x) > 1 else 0
                    )
                    
                    # Volatility (std)
                    features[f'{col}_volatility_{window}'] = metrics[col].rolling(window=window, min_periods=1).std()
        
        # Rate of change features
        for col in metrics.columns:
            if col not in ['timestamp', 'degraded', 'time_to_failure', 'severity']:
                features[f'{col}_roc'] = metrics[col].diff()
                features[f'{col}_roc_pct'] = metrics[col].pct_change()
        
        # Time-based features
        if 'timestamp' in features.columns:
            features['hour'] = pd.to_datetime(features['timestamp']).dt.hour
            features['day_of_week'] = pd.to_datetime(features['timestamp']).dt.dayofweek
            features['is_business_hours'] = features['hour'].apply(lambda x: 1 if 9 <= x <= 17 else 0)
            features.drop('timestamp', axis=1, inplace=True)
        
        # Drop target columns if present
        for col in ['degraded', 'time_to_failure', 'severity']:
            if col in features.columns:
                features.drop(col, axis=1, inplace=True)
        
        # Fill NaN values
        features.fillna(method='bfill', inplace=True)
        features.fillna(0, inplace=True)
        
        return features
    
    def prepare_labels(self, metrics: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Prepare labels for training.
        
        Returns:
            Tuple of (time_to_failure, degradation_binary, severity_class)
        """
        # Time to failure (in minutes)
        ttf = metrics['time_to_failure'].values if 'time_to_failure' in metrics else np.zeros(len(metrics))
        
        # Binary degradation label
        degraded = metrics['degraded'].values if 'degraded' in metrics else np.zeros(len(metrics))
        
        # Severity class (0: normal, 1: minor, 2: moderate, 3: severe, 4: critical)
        severity = metrics['severity'].values if 'severity' in metrics else np.zeros(len(metrics))
        
        return ttf, degraded, severity
    
    def train(self, historical_metrics: pd.DataFrame) -> Dict:
        """
        Train prediction models.
        
        Args:
            historical_metrics: Historical metrics with labels
            
        Returns:
            Training statistics
        """
        logger.info("Preparing features for training...")
        X = self.prepare_features(historical_metrics)
        self.feature_names = X.columns.tolist()
        
        ttf, degraded, severity = self.prepare_labels(historical_metrics)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Split data
        X_train, X_test, ttf_train, ttf_test, deg_train, deg_test, sev_train, sev_test = train_test_split(
            X_scaled, ttf, degraded, severity, test_size=0.2, random_state=42
        )
        
        # Train time-to-failure model
        logger.info("Training time-to-failure predictor...")
        self.ttf_model.fit(X_train, ttf_train)
        ttf_score = self.ttf_model.score(X_test, ttf_test)
        
        # Train degradation classifier
        logger.info("Training degradation classifier...")
        self.degradation_model.fit(X_train, deg_train)
        deg_score = self.degradation_model.score(X_test, deg_test)
        
        # Train severity classifier
        logger.info("Training severity classifier...")
        self.severity_model.fit(X_train, sev_train)
        sev_score = self.severity_model.score(X_test, sev_test)
        
        self.is_trained = True
        
        stats = {
            'total_samples': len(X),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'ttf_r2_score': float(ttf_score),
            'degradation_accuracy': float(deg_score),
            'severity_accuracy': float(sev_score),
            'feature_count': len(self.feature_names)
        }
        
        logger.info(f"Training complete: {json.dumps(stats, indent=2)}")
        
        return stats
    
    def predict(self, current_metrics: pd.DataFrame) -> List[Dict]:
        """
        Predict service degradation.
        
        Args:
            current_metrics: Current metrics data
            
        Returns:
            List of predictions
        """
        if not self.is_trained:
            raise ValueError("Model must be trained before prediction")
        
        X = self.prepare_features(current_metrics)
        
        # Ensure same features as training
        for col in self.feature_names:
            if col not in X.columns:
                X[col] = 0
        X = X[self.feature_names]
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Make predictions
        ttf_pred = self.ttf_model.predict(X_scaled)
        deg_prob = self.degradation_model.predict_proba(X_scaled)[:, 1]
        deg_pred = self.degradation_model.predict(X_scaled)
        sev_pred = self.severity_model.predict(X_scaled)
        
        # Prepare results
        predictions = []
        for idx in range(len(X)):
            prediction = {
                'timestamp': current_metrics.iloc[idx].get('timestamp', datetime.now().isoformat()),
                'time_to_failure_minutes': float(ttf_pred[idx]),
                'degradation_probability': float(deg_prob[idx]),
                'will_degrade': bool(deg_pred[idx]),
                'predicted_severity': self._severity_to_label(int(sev_pred[idx])),
                'risk_assessment': self._assess_risk(ttf_pred[idx], deg_prob[idx], sev_pred[idx]),
                'recommended_actions': self._recommend_actions(ttf_pred[idx], deg_prob[idx], sev_pred[idx])
            }
            predictions.append(prediction)
        
        return predictions
    
    def _severity_to_label(self, severity: int) -> str:
        """Convert severity class to label."""
        labels = {
            0: 'NORMAL',
            1: 'MINOR',
            2: 'MODERATE',
            3: 'SEVERE',
            4: 'CRITICAL'
        }
        return labels.get(severity, 'UNKNOWN')
    
    def _assess_risk(self, ttf: float, degradation_prob: float, severity: int) -> str:
        """
        Assess disaster risk based on predictions.
        
        Implements Risk = f(H, V, R) from Shi et al. (2020)
        """
        # Hazard: degradation probability
        # Vulnerability: severity level
        # Recovery: time to failure (inverse relationship)
        
        risk_score = (degradation_prob * (severity + 1)) / max(ttf, 1)
        
        if risk_score > 2.0:
            return 'EXTREME'
        elif risk_score > 1.0:
            return 'HIGH'
        elif risk_score > 0.5:
            return 'MODERATE'
        elif risk_score > 0.2:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def _recommend_actions(self, ttf: float, degradation_prob: float, severity: int) -> List[str]:
        """Recommend actions based on predictions."""
        actions = []
        
        if degradation_prob > 0.7:
            actions.append("IMMEDIATE: Initiate failover procedures")
            actions.append("IMMEDIATE: Alert on-call team")
        elif degradation_prob > 0.5:
            actions.append("URGENT: Prepare failover resources")
            actions.append("URGENT: Increase monitoring frequency")
        elif degradation_prob > 0.3:
            actions.append("WARNING: Monitor closely")
            actions.append("WARNING: Review system logs")
        
        if ttf < 5:
            actions.append("CRITICAL: Less than 5 minutes to failure")
            actions.append("CRITICAL: Execute emergency recovery plan")
        elif ttf < 15:
            actions.append("HIGH: Less than 15 minutes to failure")
            actions.append("HIGH: Prepare recovery resources")
        
        if severity >= 3:
            actions.append("SEVERE: High impact expected")
            actions.append("SEVERE: Notify stakeholders")
        
        if not actions:
            actions.append("NORMAL: Continue monitoring")
        
        return actions
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance from models."""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        # Get importance from TTF model (most comprehensive)
        importance = dict(zip(self.feature_names, self.ttf_model.feature_importances_))
        
        # Sort by importance
        sorted_importance = dict(sorted(importance.items(), key=lambda x: x[1], reverse=True))
        
        return sorted_importance
    
    def save_model(self, filepath: str):
        """Save trained models to disk."""
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        model_data = {
            'ttf_model': self.ttf_model,
            'degradation_model': self.degradation_model,
            'severity_model': self.severity_model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'prediction_horizon': self.prediction_horizon
        }
        
        joblib.dump(model_data, filepath)
        logger.info(f"Models saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load trained models from disk."""
        model_data = joblib.load(filepath)
        
        self.ttf_model = model_data['ttf_model']
        self.degradation_model = model_data['degradation_model']
        self.severity_model = model_data['severity_model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.prediction_horizon = model_data['prediction_horizon']
        self.is_trained = True
        
        logger.info(f"Models loaded from {filepath}")


def generate_sample_data_with_labels(num_samples: int = 5000) -> pd.DataFrame:
    """Generate sample data with degradation labels for training."""
    np.random.seed(42)
    
    timestamps = pd.date_range(start='2024-01-01', periods=num_samples, freq='1min')
    
    # Initialize arrays
    cpu = np.zeros(num_samples)
    memory = np.zeros(num_samples)
    latency = np.zeros(num_samples)
    error_rate = np.zeros(num_samples)
    degraded = np.zeros(num_samples)
    time_to_failure = np.zeros(num_samples)
    severity = np.zeros(num_samples)
    
    # Generate normal and degraded periods
    i = 0
    while i < num_samples:
        # Normal period
        normal_length = np.random.randint(100, 300)
        for j in range(i, min(i + normal_length, num_samples)):
            cpu[j] = np.random.normal(50, 10)
            memory[j] = np.random.normal(60, 8)
            latency[j] = np.random.normal(100, 20)
            error_rate[j] = np.random.normal(0.5, 0.2)
            degraded[j] = 0
            time_to_failure[j] = 0
            severity[j] = 0
        
        i += normal_length
        
        if i >= num_samples:
            break
        
        # Degradation period
        degradation_length = np.random.randint(20, 60)
        sev = np.random.choice([1, 2, 3, 4], p=[0.4, 0.3, 0.2, 0.1])
        
        for j in range(i, min(i + degradation_length, num_samples)):
            # Gradual degradation
            progress = (j - i) / degradation_length
            
            cpu[j] = 50 + progress * (90 - 50) + np.random.normal(0, 5)
            memory[j] = 60 + progress * (85 - 60) + np.random.normal(0, 3)
            latency[j] = 100 + progress * (1000 - 100) + np.random.normal(0, 50)
            error_rate[j] = 0.5 + progress * (10 - 0.5) + np.random.normal(0, 0.5)
            
            degraded[j] = 1
            time_to_failure[j] = degradation_length - (j - i)
            severity[j] = sev
        
        i += degradation_length
    
    data = pd.DataFrame({
        'timestamp': timestamps[:num_samples],
        'cpu_utilization': np.clip(cpu, 0, 100),
        'memory_usage': np.clip(memory, 0, 100),
        'latency_ms': np.clip(latency, 0, None),
        'error_rate': np.clip(error_rate, 0, 100),
        'degraded': degraded,
        'time_to_failure': time_to_failure,
        'severity': severity
    })
    
    return data


if __name__ == "__main__":
    # Example usage
    logger.info("Generating sample training data...")
    training_data = generate_sample_data_with_labels(num_samples=10000)
    
    logger.info(f"Training data shape: {training_data.shape}")
    logger.info(f"Degradation rate: {training_data['degraded'].mean():.2%}")
    
    logger.info("Training prediction models...")
    predictor = ServiceDegradationPredictor(prediction_horizon_minutes=15)
    stats = predictor.train(training_data)
    
    logger.info(f"Training statistics: {json.dumps(stats, indent=2)}")
    
    # Feature importance
    importance = predictor.get_feature_importance()
    logger.info("Top 10 most important features:")
    for feature, score in list(importance.items())[:10]:
        logger.info(f"  {feature}: {score:.4f}")
    
    # Save model
    predictor.save_model('degradation_predictor_model.pkl')
    
    # Test predictions
    logger.info("Testing predictions...")
    test_data = generate_sample_data_with_labels(num_samples=100)
    predictions = predictor.predict(test_data)
    
    # Show high-risk predictions
    high_risk = [p for p in predictions if p['degradation_probability'] > 0.5]
    logger.info(f"Found {len(high_risk)} high-risk predictions")
    
    for pred in high_risk[:5]:
        logger.info(f"\nPrediction: {json.dumps(pred, indent=2)}")
