from sklearn.ensemble import IsolationForest
from sentinel.collector.models import NormalizedEvent
from .features import extract_features
import joblib
import pandas as pd

class AnomalyDetector:
    def __init__(self, n_estimators = 100, contamination = 0.1, random_state = 42):
        self.model = IsolationForest(n_estimators=n_estimators, contamination=contamination, random_state=random_state)

    def train(self, events: list[NormalizedEvent]):
        feature_list = [extract_features(event) for event in events]
        X = [[f["hour"], f["day_of_week"], f["region_encoded"], f["action_encoded"], f["is_sensitive_action"]] for f in feature_list]
        self.model.fit(X)

    def score(self, event : NormalizedEvent) -> float:
        features = extract_features(event)
        X = [[features["hour"], features["day_of_week"], features["region_encoded"], features["action_encoded"], features["is_sensitive_action"]]]
        return self.model.score_samples(X)[0]
    
    def save(self, path : str):
        joblib.dump(self.model, path)

    def load(self, path : str):
        self.model = joblib.load(path)

    def table_score(self, events: list[NormalizedEvent]) -> pd.DataFrame:
        data = []
        for event in events:
            score = self.score(event)
            data.append({
                "timestamp": event.timestamp,
                "region": event.region,
                "action": event.action,
                "score": score
            })
        return pd.DataFrame(data)
    
class ScoredEvent(NormalizedEvent):
    anomaly_score : float
    is_anomaly : bool

