import pytest
from sentinel.detector.features import extract_features
from sentinel.collector.models import CloudTrailRawEvent, NormalizedEvent, normalize_event
from datetime import datetime, timezone

@pytest.fixture
def sample_raw_event(): 
        return CloudTrailRawEvent(
            eventName="ExpectedAction",
            awsRegion="ExpectedRegion",
            sourceIPAddress="ExpectedSourceIP",
            eventTime="2024-01-01T14:00:00Z",
            userIdentity={
                "userName": "ExpectedUsername",
                "arn": "ExpectedResource"
            }
        )

@pytest.fixture
def sample_raw_event2(): 
        return CloudTrailRawEvent(
            eventName="DeleteUser",
            awsRegion="us-east-1",
            sourceIPAddress="ExpectedSourceIP",
            eventTime="2024-01-01T14:00:00Z",
            userIdentity={
                "userName": "ExpectedUsername",
                "arn": "ExpectedResource"
            }
        )

def test_extract_features_returns_expected_features(sample_raw_event):
    normalized = normalize_event(sample_raw_event) 
    features = extract_features(normalized)
    assert features["action_encoded"] == 99
    assert features["region_encoded"] == 99
    assert features["is_sensitive_action"] == 0
    assert features["hour"] == 14
    assert features["day_of_week"] == 0

def test_extract_features_sensitive_action(sample_raw_event2):
    normalized = normalize_event(sample_raw_event2) 
    features = extract_features(normalized)
    assert features["action_encoded"] == 1
    assert features["region_encoded"] == 0
    assert features["is_sensitive_action"] == 1