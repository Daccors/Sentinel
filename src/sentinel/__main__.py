from sentinel.logger import configure_logging
from sentinel.streaming.consumer import KafkaConsumer
import structlog

configure_logging()
logger = structlog.get_logger()
logger.info("CloudSentinel starting...")

consumer = KafkaConsumer()
consumer.start()