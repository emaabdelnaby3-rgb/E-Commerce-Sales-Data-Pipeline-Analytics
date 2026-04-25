"""Simple event producer for user/case/donation events."""
import json
import os
from datetime import datetime

from kafka import KafkaProducer

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "kafka:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "charity_events")


def main():
    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
    )

    payload = {
        "event_type": "case_created",
        "occurred_at": datetime.utcnow().isoformat(),
        "case_id": 101,
        "organization_id": 1,
        "amount_requested": 2500,
    }
    producer.send(TOPIC, payload)
    producer.flush()


if __name__ == "__main__":
    main()
