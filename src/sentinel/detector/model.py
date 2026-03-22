from __future__ import annotations
import os
from pathlib import Path
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sentinel.collector.models import NormalizedEvent
from sentinel.detector.features import FEATURE_NAMES, extract_features, features_to_vector

DEFAULT_N_ESTIMATORS = int(os.getenv("IF_N_ESTIMATORS", "100"))
DEFAULT_CONTAMINATION = float(os.getenv("IF_CONTAMINATION", "0.1"))
DEFAULT_RANDOM_STATE = 42


class AnomalyDetector:

    def __init__(
        self,
        n_estimators: int = DEFAULT_N_ESTIMATORS,
        contamination: float = DEFAULT_CONTAMINATION,
        random_state: int = DEFAULT_RANDOM_STATE,
    ) -> None:
        self.model = IsolationForest(
            n_estimators=n_estimators,
            contamination=contamination,
            random_state=random_state,
        )
        self._is_trained = False

    def train(self, events: list[NormalizedEvent]) -> None:

        if not events:
            raise ValueError("Cannot train on an empty event list.")

        X = self._build_matrix(events)
        self.model.fit(X)
        self._is_trained = True

    def score(self, event: NormalizedEvent) -> float:
        self._assert_trained()
        features = extract_features(event)
        vector = features_to_vector(features)
        return float(self.model.score_samples([vector])[0])

    def score_batch(self, events: list[NormalizedEvent]) -> list[float]:
        self._assert_trained()
        X = self._build_matrix(events)
        return [float(s) for s in self.model.score_samples(X)]

    def save(self, path: Path) -> None:
        self._assert_trained()
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.model, path)

    @classmethod
    def load_from_path(cls, path: Path) -> AnomalyDetector:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        instance = cls.__new__(cls)
        instance.model = joblib.load(path)
        instance._is_trained = True
        return instance

    def score_table(self, events: list[NormalizedEvent], threshold: float = -0.6) -> pd.DataFrame:
        self._assert_trained()
        records = []
        for event, score in zip(events, self.score_batch(events)):
            features = extract_features(event)
            records.append({
                "timestamp": event.timestamp,
                "username": event.username,
                "region": event.region,
                "action": event.action,
                "source_ip": event.source_ip,
                "anomaly_score": round(score, 4),
                "is_anomaly": score < threshold,
                **{f: features[f] for f in FEATURE_NAMES},
            })
        return pd.DataFrame(records)
    
    def _build_matrix(self, events: list[NormalizedEvent]) -> list[list[int | float]]:
        return [features_to_vector(extract_features(e)) for e in events]

    def _assert_trained(self) -> None:
        if not self._is_trained:
            raise RuntimeError(
                "Model has not been trained. Call train() or load_from_path() first."
            )


class ScoredEvent(NormalizedEvent):
    anomaly_score: float
    is_anomaly: bool