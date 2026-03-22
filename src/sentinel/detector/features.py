from sentinel.collector.models import NormalizedEvent

REGION_ENCODING: dict[str, int] = {
    "us-east-1": 0,
    "us-west-1": 1,
    "us-west-2": 2,
    "eu-west-1": 3,
    "eu-central-1": 4,
    "ap-southeast-1": 5,
    "ap-northeast-1": 6,
}

ACTION_ENCODING: dict[str, int] = {
    "CreateUser": 0,
    "DeleteUser": 1,
    "UpdateUser": 2,
    "CreateBucket": 3,
    "DeleteBucket": 4,
    "PutObject": 5,
    "GetObject": 6,
    "DeleteObject": 7,
    "StartInstances": 8,
    "StopInstances": 9,
    "TerminateInstances": 10,
    "RunInstances": 11,
    "CreateSecurityGroup": 12,
    "DeleteSecurityGroup": 13,
    "AuthorizeSecurityGroupIngress": 14,
    "RevokeSecurityGroupIngress": 15,
    "AuthorizeSecurityGroupEgress": 16,
    "RevokeSecurityGroupEgress": 17,
    "CreateKeyPair": 18,
    "DeleteKeyPair": 19,
    "AssumeRole": 20,
    "GetCallerIdentity": 21,
    "ListUsers": 22,
    "ListRoles": 23,
    "AttachUserPolicy": 24,
    "DetachUserPolicy": 25,
}

SENSITIVE_ACTIONS: frozenset[str] = frozenset({
    "DeleteUser",
    "DeleteBucket",
    "TerminateInstances",
    "DeleteKeyPair",
    "AttachUserPolicy",       
    "AuthorizeSecurityGroupIngress",  
    "AssumeRole",             
})

RECON_ACTIONS: frozenset[str] = frozenset({
    "ListUsers",
    "ListRoles",
    "GetCallerIdentity",
    "DescribeInstances",
    "DescribeSecurityGroups",
})

_OFF_HOURS: frozenset[int] = frozenset(range(23, 24)) | frozenset(range(0, 7))

UNKNOWN_ENCODING = 99 


def extract_features(event: NormalizedEvent) -> dict[str, int | float]:

    hour = event.timestamp.hour
    is_off_hours = 1 if hour in _OFF_HOURS else 0

    return {
        "hour": hour,
        "day_of_week": event.timestamp.weekday(),
        "is_off_hours": is_off_hours,
        "is_weekend": 1 if event.timestamp.weekday() >= 5 else 0,

        "region_encoded": REGION_ENCODING.get(event.region, UNKNOWN_ENCODING),

        "action_encoded": ACTION_ENCODING.get(event.action, UNKNOWN_ENCODING),
        "is_sensitive_action": 1 if event.action in SENSITIVE_ACTIONS else 0,
        "is_recon_action": 1 if event.action in RECON_ACTIONS else 0,

        "is_sensitive_off_hours": (
            1 if event.action in SENSITIVE_ACTIONS and is_off_hours else 0
        ),
    }


FEATURE_NAMES: list[str] = [
    "hour",
    "day_of_week",
    "is_off_hours",
    "is_weekend",
    "region_encoded",
    "action_encoded",
    "is_sensitive_action",
    "is_recon_action",
    "is_sensitive_off_hours",
]


def features_to_vector(features: dict[str, int | float]) -> list[int | float]:

    return [features[name] for name in FEATURE_NAMES]