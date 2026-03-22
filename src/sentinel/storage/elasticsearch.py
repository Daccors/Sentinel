import os
import structlog
from elasticsearch import Elasticsearch, ConnectionError, TransportError
from sentinel.collector.models import NormalizedEvent
from sentinel.detector.model import ScoredEvent

logger = structlog.get_logger()

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
INDEX_EVENTS = "cloudsentinel-events"
INDEX_ANOMALIES = "cloudsentinel-anomalies"


class ElasticSearchClient:

    def __init__(self, url: str = ELASTICSEARCH_URL) -> None:
        self.client = Elasticsearch(url)
        logger.info("Elasticsearch client initialized", url=url)

    def index_event(self, event: NormalizedEvent) -> None:
        try:
            self.client.index(
                index=INDEX_EVENTS,
                document=event.model_dump(mode="json"),
            )
            logger.debug(
                "Event indexed",
                action=event.action,
                username=event.username,
            )
        except ConnectionError as e:
            logger.error(
                "Elasticsearch unreachable, event not indexed",
                index=INDEX_EVENTS,
                action=event.action,
                error=str(e),
            )
            raise
        except TransportError as e:
            logger.error(
                "Failed to index event",
                index=INDEX_EVENTS,
                action=event.action,
                error=str(e),
            )
            raise

    def index_anomaly(self, scored_event: ScoredEvent) -> None:
        try:
            self.client.index(
                index=INDEX_ANOMALIES,
                document=scored_event.model_dump(mode="json"),
            )
            logger.warning(
                "Anomaly indexed",
                action=scored_event.action,
                username=scored_event.username,
                score=round(scored_event.anomaly_score, 4),
            )
        except (ConnectionError, TransportError) as e:
            logger.error(
                "Failed to index anomaly",
                index=INDEX_ANOMALIES,
                action=scored_event.action,
                error=str(e),
            )
            raise