import json

import pika
from pika import BasicProperties


def run_helium_blackbox(rabbit: pika.BlockingConnection, user_id: int, level: int = 1):
    with rabbit.channel() as chan:
        msg = json.dumps({
            "destination": "remote",
            "maxCatLevel": level,
            "userId": user_id,
        })
        chan.basic_publish(
            "tasks", "helium_blackbox", msg.encode(),
            BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
        )
