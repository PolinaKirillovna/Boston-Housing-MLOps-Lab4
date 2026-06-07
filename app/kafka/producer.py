"""Kafka producer for prediction events.

Publishes the result of each model prediction to a Kafka topic. The producer
is a standalone module/class so it can be reused and tested independently of
the FastAPI application. Publishing is best-effort: if the broker is
unavailable the API request still succeeds.
"""

import json
import logging
from typing import Optional

from app.kafka.settings import KafkaSettings

logger = logging.getLogger(__name__)


class PredictionProducer:
    """Publishes prediction events to a Kafka topic."""

    def __init__(self, settings: Optional[KafkaSettings] = None) -> None:
        self.settings = settings or KafkaSettings()
        self._producer = None

    def start(self) -> None:
        """Create the underlying producer and ensure the topic exists."""
        from confluent_kafka import Producer

        self._producer = Producer({"bootstrap.servers": self.settings.bootstrap_servers})
        self._ensure_topic()
        logger.info(
            "Kafka producer started for topic '%s' (%d partitions) at %s",
            self.settings.topic,
            self.settings.num_partitions,
            self.settings.bootstrap_servers,
        )

    def _ensure_topic(self) -> None:
        """Create the topic with the configured number of partitions."""
        from confluent_kafka import KafkaException
        from confluent_kafka.admin import AdminClient, NewTopic

        admin = AdminClient({"bootstrap.servers": self.settings.bootstrap_servers})
        existing = admin.list_topics(timeout=10).topics
        if self.settings.topic in existing:
            return

        new_topic = NewTopic(
            self.settings.topic,
            num_partitions=self.settings.num_partitions,
            replication_factor=1,
        )
        for topic, future in admin.create_topics([new_topic]).items():
            try:
                future.result()
                logger.info("Created Kafka topic '%s'", topic)
            except KafkaException as exc:
                # Topic may have been created concurrently; ignore that case.
                logger.warning("Could not create topic '%s': %s", topic, exc)

    def publish(self, message: dict) -> None:
        """Publish a message (best-effort, never raises to the caller)."""
        if self._producer is None:
            return

        from confluent_kafka import KafkaException

        try:
            payload = json.dumps(message, default=str).encode("utf-8")
            key = str(message.get("request_id", "")).encode("utf-8")
            self._producer.produce(self.settings.topic, key=key, value=payload)
            self._producer.poll(0)
        except (KafkaException, BufferError, ValueError) as exc:
            logger.warning("Failed to publish prediction event: %s", exc)

    def close(self) -> None:
        """Flush and release the producer."""
        if self._producer is None:
            return
        self._producer.flush(5)
        self._producer = None
        logger.info("Kafka producer closed")
