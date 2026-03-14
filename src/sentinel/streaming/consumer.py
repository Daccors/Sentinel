from confluent_kafka import Consumer
import json
from sentinel.streaming.producer import KAFKA_URL
import structlog
from sentinel.storage.elasticsearch import ElasticSearchClient
from sentinel.collector.models import CloudTrailRawEvent, NormalizedEvent, normalize_event
from sentinel.detector.model import AnomalyDetector, ScoredEvent
import random


logger = structlog.get_logger()

class KafkaConsumer:
    def __init__(self):
        self.conf = {
            'bootstrap.servers':KAFKA_URL,
            'group.id':'cloudsentinel-consumer',
            'auto.offset.reset':'earliest'
        }
        self.consumer = Consumer(self.conf)
        self.es_client = ElasticSearchClient()

        actions = ["GetObject", "PutObject", "ListBuckets", "GetObject", "GetObject"]
        regions = ["us-east-1", "us-east-1", "us-east-1", "us-west-2", "us-east-1"]

        training_events = []
        for i in range(100):
            raw = CloudTrailRawEvent(
            eventName=random.choice(actions),
            awsRegion=random.choice(regions),
            sourceIPAddress="192.0.2.0",
            eventTime=f"2024-01-{(i%28)+1:02d}T{random.randint(8,18):02d}:00:00Z",
            userIdentity={"userName": "Mateo", "arn": "arn:aws:iam::123456789012:user/Mateo"}
        )
            training_events.append(normalize_event(raw))

        self.detector = AnomalyDetector()
        self.detector.train(training_events)
    
    def start(self):
        self.consumer.subscribe(['cloudtrail-events'])
        try:
            while True:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    logger.error("Consumer error", error=msg.error())
                    continue
                    
                event_data = json.loads(msg.value().decode('utf-8'))
                normalized = NormalizedEvent(**event_data)
                self.es_client.index_event(normalized)
                logger.info("Received event", event_data=event_data)
                
                score = self.detector.score(normalized)
                scored = ScoredEvent(**normalized.model_dump(), anomaly_score=score, is_anomaly=score < -0.6)

                if scored.is_anomaly:
                    logger.warning("Anomaly detected", event_data=normalized.model_dump(), score=score)
                    self.es_client.index_anomaly(scored)

        finally:
            self.consumer.close()