from sentinel.collector.models import NormalizedEvent

REGION_ENCODING = {
    "us-east-1": 0,
    "us-west-2": 1,
    "eu-west-1": 2,
    "ap-southeast-1": 3,
}

ACTION_ENCODING = {
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
}

SENSITIVE_ACTIONS = {"DeleteUser", "DeleteBucket", "TerminateInstances"}

def extract_features(event : NormalizedEvent) -> dict:
    features = {
        "hour" : event.timestamp.hour,
        "day_of_week" : event.timestamp.weekday(),
        "region_encoded" : REGION_ENCODING.get(event.region, 99),
        "action_encoded" : ACTION_ENCODING.get(event.action, 99),
        "is_sensitive_action" : 1 if event.action in ["DeleteUser", "DeleteBucket", "TerminateInstances"] else 0
    }
    return features