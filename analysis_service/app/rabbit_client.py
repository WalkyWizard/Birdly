import json
import os
import pika
from typing import Dict, Any

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@127.0.0.1:5672/")

def publish_notification(message: Dict[str, Any], queue_name: str = "birdly_notifications") -> bool:
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=json.dumps(message, ensure_ascii=False).encode("utf-8"),
            properties=pika.BasicProperties(
                delivery_mode=2,
                content_type="application/json"
            )
        )
        connection.close()
        return True
    except Exception:
        return False
