from datetime import datetime
from typing import Optional
import structlog
from pydantic import BaseModel, Field, ValidationError
from sentinel.exceptions import NormalizationError

logger = structlog.get_logger()

class UserIdentity(BaseModel):
    type: Optional[str] = None 
    userName: Optional[str] = None
    arn: Optional[str] = None
    accountId: Optional[str] = None
    principalId: Optional[str] = None

    @property
    def resolved_username(self) -> str:
        return self.userName or self.principalId or self.type or "Unknown"


class CloudTrailRawEvent(BaseModel):
    eventName: str
    awsRegion: str
    sourceIPAddress: str
    eventTime: datetime
    userIdentity: UserIdentity
    eventSource: Optional[str] = None          
    requestParameters: Optional[dict] = None   
    errorCode: Optional[str] = None           
    errorMessage: Optional[str] = None

class NormalizedEvent(BaseModel):
    action: str
    region: str
    source_ip: str
    timestamp: datetime
    username: str
    resource: Optional[str] = None
    event_source: Optional[str] = None
    error_code: Optional[str] = None
    is_failed_call: bool = Field(default=False)

def normalize_event(raw_event: CloudTrailRawEvent) -> NormalizedEvent:
    try:
        normalized = NormalizedEvent(
            action=raw_event.eventName,
            region=raw_event.awsRegion,
            source_ip=raw_event.sourceIPAddress,
            timestamp=raw_event.eventTime,
            username=raw_event.userIdentity.resolved_username,
            resource=raw_event.userIdentity.arn,
            event_source=raw_event.eventSource,
            error_code=raw_event.errorCode,
            is_failed_call=raw_event.errorCode is not None,
        )
    except ValidationError as e:
        logger.error(
            "Failed to normalize event",
            event_name=raw_event.eventName,
            error=str(e),
        )
        raise NormalizationError("Failed to normalize event", errors=e.errors())

    logger.info(
        "Event normalized",
        action=normalized.action,
        username=normalized.username,
        region=normalized.region,
        is_failed_call=normalized.is_failed_call,
    )
    return normalized