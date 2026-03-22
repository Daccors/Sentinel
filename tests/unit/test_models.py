import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
from sentinel.collector.models import (
    CloudTrailRawEvent,
    NormalizedEvent,
    UserIdentity,
    normalize_event,
)
from sentinel.exceptions import NormalizationError

@pytest.fixture
def sample_raw_event() -> CloudTrailRawEvent:
    return CloudTrailRawEvent(
        eventName="ExpectedAction",
        awsRegion="ExpectedRegion",
        sourceIPAddress="ExpectedSourceIP",
        eventTime="2024-01-01T00:00:00Z",
        userIdentity=UserIdentity(
            userName="ExpectedUsername",
            arn="ExpectedResource",
        ),
    )


@pytest.fixture
def iam_event() -> CloudTrailRawEvent:
    return CloudTrailRawEvent(
        eventName="CreateUser",
        awsRegion="us-east-1",
        sourceIPAddress="203.0.113.42",
        eventTime="2024-06-15T22:30:00Z",
        eventSource="iam.amazonaws.com",
        userIdentity=UserIdentity(userName="alice", arn="arn:aws:iam::123:user/alice"),
    )


@pytest.fixture
def failed_event() -> CloudTrailRawEvent:
    return CloudTrailRawEvent(
        eventName="AssumeRole",
        awsRegion="eu-west-1",
        sourceIPAddress="198.51.100.5",
        eventTime="2024-06-15T03:00:00Z",
        userIdentity=UserIdentity(userName="bob"),
        errorCode="AccessDenied",
        errorMessage="User is not authorized to perform sts:AssumeRole",
    )

def test_normalize_fields(sample_raw_event):
    normalized = normalize_event(sample_raw_event)
    assert normalized.action == "ExpectedAction"
    assert normalized.region == "ExpectedRegion"
    assert normalized.source_ip == "ExpectedSourceIP"
    assert normalized.timestamp == datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
    assert normalized.username == "ExpectedUsername"
    assert normalized.resource == "ExpectedResource"


def test_normalize_event_source(iam_event):
    normalized = normalize_event(iam_event)
    assert normalized.event_source == "iam.amazonaws.com"


def test_normalize_is_failed_call_false(iam_event):
    normalized = normalize_event(iam_event)
    assert normalized.is_failed_call is False


def test_normalize_is_failed_call_true(failed_event):
    normalized = normalize_event(failed_event)
    assert normalized.is_failed_call is True
    assert normalized.error_code == "AccessDenied"

def test_missing_username_falls_back_to_unknown():
    event = CloudTrailRawEvent(
        eventName="GetObject",
        awsRegion="us-east-1",
        sourceIPAddress="10.0.0.1",
        eventTime="2024-01-01T00:00:00Z",
        userIdentity=UserIdentity(),
    )
    normalized = normalize_event(event)
    assert normalized.username == "Unknown"


def test_missing_resource_is_none():
    event = CloudTrailRawEvent(
        eventName="GetObject",
        awsRegion="us-east-1",
        sourceIPAddress="10.0.0.1",
        eventTime="2024-01-01T00:00:00Z",
        userIdentity=UserIdentity(userName="carol"),
    )
    normalized = normalize_event(event)
    assert normalized.resource is None


def test_principal_id_used_when_no_username():
    event = CloudTrailRawEvent(
        eventName="AssumeRole",
        awsRegion="us-east-1",
        sourceIPAddress="10.0.0.1",
        eventTime="2024-01-01T00:00:00Z",
        userIdentity=UserIdentity(principalId="AROA1234567890EXAMPLE"),
    )
    normalized = normalize_event(event)
    assert normalized.username == "AROA1234567890EXAMPLE"


def test_type_used_as_last_resort():
    event = CloudTrailRawEvent(
        eventName="GetObject",
        awsRegion="us-east-1",
        sourceIPAddress="10.0.0.1",
        eventTime="2024-01-01T00:00:00Z",
        userIdentity=UserIdentity(type="Root"),
    )
    normalized = normalize_event(event)
    assert normalized.username == "Root"

def test_invalid_date_raises_validation_error():
    with pytest.raises(ValidationError):
        CloudTrailRawEvent(
            eventName="GetObject",
            awsRegion="us-east-1",
            sourceIPAddress="10.0.0.1",
            eventTime="not-a-date",
            userIdentity=UserIdentity(userName="alice"),
        )


def test_missing_required_field_raises_validation_error():
    with pytest.raises(ValidationError):
        CloudTrailRawEvent(
            awsRegion="us-east-1",
            sourceIPAddress="10.0.0.1",
            eventTime="2024-01-01T00:00:00Z",
            userIdentity=UserIdentity(userName="alice"),
        )