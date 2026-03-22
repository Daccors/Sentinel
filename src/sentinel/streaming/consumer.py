import json
import os
import time

import structlog
from confluent_kafka import Consumer, KafkaError, KafkaException

from sentinel.collector.models import CloudTrailRawEvent, NormalizedEvent, normalize_event
from sentinel.detector.model import AnomalyDetector, ScoredEvent
from sentinel.storage.elasticsearch import ElasticSearchClient

logger = structlog.get_logger()

KAFKA_URL = os.getenv("KAFKA_URL", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "cloudtrail-events")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "cloudsentinel-consumer")
ANOMALY_THRESHOLD = float(os.getenv("ANOMALY_THRESHOLD", "-0.6"))
MAX_RETRY_ATTEMPTS = int(os.getenv("KAFKA_MAX_RETRY", "5"))
RETRY_DELAY_SECONDS = int(os.getenv("KAFKA_RETRY_DELAY", "3"))


class KafkaConsumer:

    def __init__(self, detector: AnomalyDetector) -> None:
        self.conf = {
            "bootstrap.servers": KAFKA_URL,
            "group.id": KAFKA_GROUP_ID,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
        self.consumer = Consumer(self.conf)
        self.es_client = ElasticSearchClient()
        self.detector = detector
        self._running = False

    def _connect_with_retry(self) -> None:
        for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
            try:
                self.consumer.subscribe([KAFKA_TOPIC])
                logger.info("Subscribed to Kafka topic", topic=KAFKA_TOPIC)
                return
            except KafkaException as e:
                logger.warning(
                    "Kafka subscription failed, retrying",
                    attempt=attempt,
                    max_attempts=MAX_RETRY_ATTEMPTS,
                    error=str(e),
                )
                time.sleep(RETRY_DELAY_SECONDS * attempt)

        raise RuntimeError(
            f"Could not subscribe to Kafka after {MAX_RETRY_ATTEMPTS} attempts"
        )

    def _process_message(self, raw_value: bytes) -> None:
        event_data = json.loads(raw_value.decode("utf-8"))

        if "eventName" in event_data:
            raw = CloudTrailRawEvent(**event_data)
            normalized = normalize_event(raw)
        else:
            normalized = NormalizedEvent(**event_data)

        self.es_client.index_event(normalized)

        score = self.detector.score(normalized)
        is_anomaly = score < ANOMALY_THRESHOLD
        scored = ScoredEvent(
            **normalized.model_dump(),
            anomaly_score=score,
            is_anomaly=is_anomaly,
        )

        if scored.is_anomaly:
            logger.warning(
                "Anomaly detected",
                action=normalized.action,
                username=normalized.username,
                region=normalized.region,
                score=round(score, 4),
                threshold=ANOMALY_THRESHOLD,
            )
            self.es_client.index_anomaly(scored)

    def start(self) -> None:
        self._connect_with_retry()
        self._running = True

        logger.info("Consumer started", topic=KAFKA_TOPIC, threshold=ANOMALY_THRESHOLD)

        try:
            while self._running:
                msg = self.consumer.poll(timeout=1.0)

                if msg is None:
                    continue

                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    logger.error("Kafka consumer error", error=msg.error())
                    continue

                try:
                    self._process_message(msg.value())
                    self.consumer.commit(message=msg)
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(
                        "Failed to process message, skipping",
                        error=str(e),
                        raw_value=msg.value()[:200],
                    )
                except Exception as e:
                    logger.error("Unexpected error processing message", error=str(e))

        finally:
            self.consumer.close()
            logger.info("Consumer closed")

    def stop(self) -> None:
        self._running = False