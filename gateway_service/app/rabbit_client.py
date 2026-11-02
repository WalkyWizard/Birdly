import json
import os
import pika
from typing import Dict, Any, List

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@127.0.0.1:5672/")

def publish_message(message: Dict[str, Any], queue_name: str = "birdly_notifications") -> bool:
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

def consume_messages(queue_name: str = "birdly_notifications", max_messages: int = 10) -> List[Dict[str, Any]]:
    messages = []
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)

        for _ in range(max_messages):
            method_frame, header_frame, body = channel.basic_get(queue=queue_name, auto_ack=True)
            if method_frame:
                try:
                    data = json.loads(body.decode("utf-8"))
                    messages.append(data)
                except Exception:
                    messages.append({"raw": body.decode("utf-8", errors="ignore")})
            else:
                break

        connection.close()
    except Exception:
        pass
    return messages

def get_queue_info(queue_name: str = "birdly_notifications") -> Dict[str, Any]:
    try:
        params = pika.URLParameters(RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        res = channel.queue_declare(queue=queue_name, durable=True, passive=True)
        count = res.method.message_count
        connection.close()
        return {"status": "connected", "queue": queue_name, "message_count": count}
    except Exception as exc:
        return {"status": "disconnected", "queue": queue_name, "error": str(exc)}
