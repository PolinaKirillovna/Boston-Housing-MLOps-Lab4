"""Kafka consumer for prediction events.

A small OOP consumer that subscribes to the predictions topic and handles each
message. It runs as a separate service (see scripts/run_consumer.py and the
`consumer` service in docker-compose.yml).
"""

import json
import logging
from typing import Optional

from app.kafka.settings import KafkaSettings

logger = logging.getLogger(__name__)


class PredictionConsumer:
    """Consumes prediction events from a Kafka topic."""

    def __init__(self, settings: Optional[KafkaSettings] = None) -> None:
        self.settings = settings or KafkaSettings()
        self._consumer = None
        self._running = False

    def start(self) -> None:
        """Create the underlying consumer and subscribe to the topic."""
        from confluent_kafka import Consumer

        self._consumer = Consumer(
            {
                "bootstrap.servers": self.settings.bootstrap_servers,
                "group.id": self.settings.consumer_group,
                "auto.offset.reset": "earliest",
                "enable.auto.commit": True,
            }
        )
        self._consumer.subscribe([self.settings.topic])
        logger.info(
            "Kafka consumer subscribed to '%s' (group '%s') at %s",
            self.settings.topic,
            self.settings.consumer_group,
            self.settings.bootstrap_servers,
        )

    def handle_message(self, message: dict) -> None:
        """Process a single decoded message. Override for custom behaviour."""
        logger.info("Received prediction event: %s", message)
        print(f"[consumer] prediction event: {message}", flush=True)

    def run(self) -> None:
        """Poll the topic and dispatch messages until interrupted."""
        from confluent_kafka import KafkaError, KafkaException

        if self._consumer is None:
            self.start()
        self._running = True

        try:
            while self._running:
                msg = self._consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    raise KafkaException(msg.error())
                try:
                    data = json.loads(msg.value().decode("utf-8"))
                except (ValueError, UnicodeDecodeError) as exc:
                    logger.warning("Skipping malformed message: %s", exc)
                    continue
                self.handle_message(data)
        except KeyboardInterrupt:
            logger.info("Consumer interrupted, shutting down")
        finally:
            self.stop()

    def stop(self) -> None:
        """Close the consumer."""
        self._running = False
        if self._consumer is not None:
            self._consumer.close()
            self._consumer = None
            logger.info("Kafka consumer closed")
