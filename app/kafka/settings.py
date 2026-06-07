"""Kafka configuration for the model service.

Values come from the [kafka] section of config.ini and can be overridden via
environment variables (handy inside docker-compose). The topic name and the
number of partitions are configuration, never hard-coded in the producer or
consumer.
"""

import os
from configparser import ConfigParser
from typing import Optional

from src.config import load_config


class KafkaSettings:
    """Typed access to Kafka configuration."""

    def __init__(self, config: Optional[ConfigParser] = None) -> None:
        config = config or load_config()
        section = config["kafka"]

        self.bootstrap_servers = os.getenv(
            "KAFKA_BOOTSTRAP_SERVERS", section["bootstrap_servers"]
        )
        self.topic = os.getenv("KAFKA_TOPIC", section["topic"])
        self.num_partitions = int(
            os.getenv("KAFKA_NUM_PARTITIONS", section["num_partitions"])
        )
        self.consumer_group = os.getenv(
            "KAFKA_CONSUMER_GROUP", section["consumer_group"]
        )

    def __repr__(self) -> str:
        return (
            f"KafkaSettings(bootstrap_servers={self.bootstrap_servers!r}, "
            f"topic={self.topic!r}, num_partitions={self.num_partitions}, "
            f"consumer_group={self.consumer_group!r})"
        )
