from confluent_kafka import Producer
from sentinel.collector.models import NormalizedEvent
import structlog

logger = structlog.get_logger()

KAFKA_URL = 'localhost:9092'

class KafkaProducer:
    def __init__(self):
        self.conf = {'bootstrap.servers': KAFKA_URL}
        self.producer = Producer(self.conf)

    def publish_event(self, event):
        self.producer.produce('cloudtrail-events', event.model_dump_json().encode('utf-8'), on_delivery=self.delivery_callback)
        self.producer.flush()

    def delivery_callback(self, err, msg):
        if err:
            logger.error(f'Message failed delivery: {err}')
        else:
            logger.info(f'Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}')