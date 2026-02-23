from sentinel.logger import configure_logging
import structlog

configure_logging()
logger = structlog.get_logger()
logger.info("CloudSentinel starting...")