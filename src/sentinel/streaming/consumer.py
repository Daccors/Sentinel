from confluent_kafka import Consumer
import json
from sentinel.streaming.producer import KAFKA_URL
import structlog
from sentinel.storage.elasticsearch import ElasticSearchClient
from sentinel.collector.models import NormalizedEvent

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

        finally:
            self.consumer.close()