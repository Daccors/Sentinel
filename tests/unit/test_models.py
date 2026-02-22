import pytest
from sentinel.collector.models import CloudTrailRawEvent, NormalizedEvent, normalize_event
from sentinel.exceptions import NormalizationError
from pydantic import ValidationError
from datetime import datetime, timezone

@pytest.fixture
def sample_raw_event(): 
        return CloudTrailRawEvent(
            eventName="ExpectedAction",
            awsRegion="ExpectedRegion",
            sourceIPAddress="ExpectedSourceIP",
            eventTime="2024-01-01T00:00:00Z",
            userIdentity={
                "userName": "ExpectedUsername",
                "arn": "ExpectedResource"
            }
        )

def test_normalize_fields(sample_raw_event):
    normalized = normalize_event(sample_raw_event)
    assert normalized.action == "ExpectedAction"
    assert normalized.region == "ExpectedRegion"
    assert normalized.source_ip == "ExpectedSourceIP"
    assert normalized.timestamp == datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert normalized.username == "ExpectedUsername"
    assert normalized.resource == "ExpectedResource"

def test_normalizationError():
    with pytest.raises(ValidationError):
        CloudTrailRawEvent(
            eventName="ExpectedAction",
            awsRegion="ExpectedRegion",
            sourceIPAddress="ExpectedSourceIP",
            eventTime="InvalidDate",
            userIdentity={
                "userName": "ExpectedUsername",
                "arn": "ExpectedResource"
            }
        )

def test_missing_username(sample_raw_event):
    sample_raw_event.userIdentity.pop("userName")
    normalized = normalize_event(sample_raw_event)
    assert normalized.username == "Unknown"

def test_missing_resource(sample_raw_event):
    sample_raw_event.userIdentity.pop("arn")
    normalized = normalize_event(sample_raw_event)
    assert normalized.resource is None
