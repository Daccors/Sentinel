import pytest
from datetime import datetime, timezone
from sentinel.collector.models import CloudTrailRawEvent, UserIdentity, normalize_event
from sentinel.detector.features import (
    FEATURE_NAMES,
    SENSITIVE_ACTIONS,
    RECON_ACTIONS,
    extract_features,
    features_to_vector,
)

def make_event(
    action: str = "GetObject",
    region: str = "us-east-1",
    hour: int = 14,
    weekday: int = 0,
    ) -> object:
    base_dates = {0: "2024-01-01", 1: "2024-01-02", 2: "2024-01-03",
                  3: "2024-01-04", 4: "2024-01-05", 5: "2024-01-06", 6: "2024-01-07"}
    date_str = base_dates[weekday]
    raw = CloudTrailRawEvent(
        eventName=action,
        awsRegion=region,
        sourceIPAddress="10.0.0.1",
        eventTime=f"{date_str}T{hour:02d}:00:00Z",
        userIdentity=UserIdentity(userName="test-user"),
    )
    return normalize_event(raw)

def test_known_region_is_encoded():
    event = make_event(region="us-east-1")
    assert extract_features(event)["region_encoded"] == 0


def test_unknown_region_returns_sentinel_value():
    event = make_event(region="unknown-region-99")
    assert extract_features(event)["region_encoded"] == 99


def test_known_action_is_encoded():
    event = make_event(action="DeleteUser")
    assert extract_features(event)["action_encoded"] == 1


def test_unknown_action_returns_sentinel_value():
    event = make_event(action="SomeNewAWSAction")
    assert extract_features(event)["action_encoded"] == 99


def test_hour_extracted_correctly():
    event = make_event(hour=14)
    assert extract_features(event)["hour"] == 14


def test_day_of_week_monday():
    event = make_event(weekday=0)
    assert extract_features(event)["day_of_week"] == 0


def test_day_of_week_saturday():
    event = make_event(weekday=5)
    assert extract_features(event)["day_of_week"] == 5

def test_sensitive_action_flag_is_set():
    for action in SENSITIVE_ACTIONS:
        event = make_event(action=action)
        assert extract_features(event)["is_sensitive_action"] == 1, (
            f"Expected is_sensitive_action=1 for action '{action}'"
        )


def test_non_sensitive_action_flag_is_zero():
    event = make_event(action="GetObject")
    assert extract_features(event)["is_sensitive_action"] == 0

def test_recon_action_flag_is_set():
    for action in RECON_ACTIONS:
        event = make_event(action=action)
        assert extract_features(event)["is_recon_action"] == 1, (
            f"Expected is_recon_action=1 for action '{action}'"
        )


def test_non_recon_action_flag_is_zero():
    event = make_event(action="PutObject")
    assert extract_features(event)["is_recon_action"] == 0

def test_off_hours_flag_at_midnight():
    event = make_event(hour=0)
    assert extract_features(event)["is_off_hours"] == 1


def test_off_hours_flag_at_3am():
    event = make_event(hour=3)
    assert extract_features(event)["is_off_hours"] == 1


def test_off_hours_flag_at_11pm():
    event = make_event(hour=23)
    assert extract_features(event)["is_off_hours"] == 1


def test_not_off_hours_during_business_hours():
    event = make_event(hour=14)
    assert extract_features(event)["is_off_hours"] == 0


def test_weekend_flag_on_saturday():
    event = make_event(weekday=5)
    assert extract_features(event)["is_weekend"] == 1


def test_weekend_flag_on_sunday():
    event = make_event(weekday=6)
    assert extract_features(event)["is_weekend"] == 1


def test_not_weekend_on_monday():
    event = make_event(weekday=0)
    assert extract_features(event)["is_weekend"] == 0

def test_sensitive_off_hours_both_true():
    event = make_event(action="DeleteUser", hour=3)
    features = extract_features(event)
    assert features["is_sensitive_action"] == 1
    assert features["is_off_hours"] == 1
    assert features["is_sensitive_off_hours"] == 1


def test_sensitive_off_hours_only_sensitive():
    event = make_event(action="DeleteUser", hour=14)
    assert extract_features(event)["is_sensitive_off_hours"] == 0


def test_sensitive_off_hours_only_off_hours():
    event = make_event(action="GetObject", hour=3)
    assert extract_features(event)["is_sensitive_off_hours"] == 0

def test_features_to_vector_length_matches_feature_names():
    event = make_event()
    features = extract_features(event)
    vector = features_to_vector(features)
    assert len(vector) == len(FEATURE_NAMES)


def test_features_to_vector_order_is_stable():
    event = make_event(action="DeleteUser", region="eu-west-1", hour=2)
    v1 = features_to_vector(extract_features(event))
    v2 = features_to_vector(extract_features(event))
    assert v1 == v2


def test_features_to_vector_values_match_dict():
    event = make_event(action="DeleteUser", region="us-east-1", hour=14)
    features = extract_features(event)
    vector = features_to_vector(features)
    for i, name in enumerate(FEATURE_NAMES):
        assert vector[i] == features[name], (
            f"Mismatch at position {i} ('{name}'): vector={vector[i]}, dict={features[name]}"
        )