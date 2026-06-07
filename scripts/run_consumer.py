"""Entrypoint for the standalone Kafka consumer service."""

import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.kafka.consumer import PredictionConsumer  # noqa: E402


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    PredictionConsumer().run()


if __name__ == "__main__":
    main()
