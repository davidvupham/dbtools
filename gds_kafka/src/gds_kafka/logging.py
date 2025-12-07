import logging
import time

from .producer import KafkaProducerClient


class KafkaLoggingHandler(logging.Handler):
    """Stream Python logs to Kafka topic."""

    def __init__(self, producer: KafkaProducerClient, topic: str = "logs"):
        super().__init__()
        self.producer = producer
        self.topic = topic

    def emit(self, record: logging.LogRecord):
        try:
            msg = self.format(record)
            payload = {
                "timestamp": time.time(),
                "logger": record.name,
                "level": record.levelname,
                "message": msg,
                "path": record.pathname,
                "lineno": record.lineno,
            }
            self.producer.send(self.topic, payload)
        except Exception:
            self.handleError(record)
