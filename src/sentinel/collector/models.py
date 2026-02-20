from pydantic import BaseModel, ValidationError
from datetime import datetime
from typing import Optional
from sentinel.exceptions import NormalizationError
import structlog

logger = structlog.get_logger()

class CloudTrailRawEvent(BaseModel):
    eventName: str
    awsRegion: str
    sourceIPAddress: str
    eventTime: datetime
    userIdentity: dict

class NormalizedEvent(BaseModel):
    action: str
    region: str
    source_ip: str
    timestamp: datetime
    username: str
    resource: Optional[str] = None

def normalize_event(raw_event: CloudTrailRawEvent) -> NormalizedEvent:

    username = raw_event.userIdentity.get('userName', 'Unknown')
    resource = raw_event.userIdentity.get('arn', None)
    
    try:
        logger.info("Successfully normalized event", action=raw_event.eventName, username=username )
        return NormalizedEvent(
            action=raw_event.eventName,
            region=raw_event.awsRegion,
            source_ip=raw_event.sourceIPAddress,
            timestamp=raw_event.eventTime,
            username=username,
            resource=resource
        )
    except ValidationError as e:
        logger.error("Failed to normalize event", error=str(e))
        raise NormalizationError("Failed to normalize event", errors=e.errors())