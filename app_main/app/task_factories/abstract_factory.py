from abc import ABC

import orjson
from pika import BasicProperties, DeliveryMode
from pika.adapters.blocking_connection import BlockingChannel
from pydantic import BaseModel
from pymongo import MongoClient


class AbstractFactory(ABC):
    def __init__(self, db: MongoClient, channel: BlockingChannel):
        self._db = db
        self._channel = channel
        self._post_init()

    def _post_init(self):
        pass

    def _basic_publish(self, exchange: str, routing_key: str, body: BaseModel, priority: int = 0):
        self._channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=orjson.dumps(body.model_dump()),
            properties=BasicProperties(delivery_mode=DeliveryMode.Persistent, priority=priority or None),
        )
