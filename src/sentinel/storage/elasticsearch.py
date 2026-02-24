import elasticsearch
import os
from sentinel.collector.models import NormalizedEvent
import structlog

logger = structlog.get_logger()

URL = os.getenv('ELASTICSEARCH_URL', "http://localhost:9200")

class ElasticSearchClient:
    def __init__(self, url= URL):
        self.client = elasticsearch.Elasticsearch(url)
    
    def index_event(self,event):
        self.client.index(index = 'cloudsentinel-events', document = event.model_dump(mode="json"))
        logger.info("Event indexed successfully", action=event.action, username=event.username )
        