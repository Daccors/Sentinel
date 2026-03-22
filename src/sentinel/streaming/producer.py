import os
import structlog
from confluent_kafka import Producer, KafkaException
from sentinel.collector.models import NormalizedEvent

logger = structlog.get_logger()

KAFKA_URL = os.getenv("KAFKA_URL", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "cloudtrail-events")


class KafkaProducer:

    def __init__(self, kafka_url: str = KAFKA_URL) -> None:
        self.topic = KAFKA_TOPIC
        try:
            self.producer = Producer({"bootstrap.servers": kafka_url})
            logger.info("Kafka producer initialized", url=kafka_url, topic=self.topic)
        except KafkaException as e:
            logger.error("Failed to initialize Kafka producer", error=str(e))
            raise

    def publish_event(self, event: NormalizedEvent) -> None:
        try:
            self.producer.produce(
                topic=self.topic,
                value=event.model_dump_json().encode("utf-8"),
                on_delivery=self._delivery_callback,
            )
            self.producer.flush()
        except KafkaException as e:
            logger.error(
                "Failed to publish event",
                action=event.action,
                username=event.username,
                error=str(e),
            )
            raise

    def _delivery_callback(self, err, msg) -> None:
        if err:
            logger.error(
                "Message delivery failed",
                topic=msg.topic(),
                error=str(err),
            )
        else:
            logger.debug(
                "Message delivered",
                topic=msg.topic(),
                partition=msg.partition(),
                offset=msg.offset(),
            )