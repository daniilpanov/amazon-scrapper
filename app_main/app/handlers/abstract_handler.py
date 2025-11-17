import json
from abc import ABC, abstractmethod
from typing import Callable

from pika import BasicProperties
from pika.spec import PERSISTENT_DELIVERY_MODE, TRANSIENT_DELIVERY_MODE


class AbstractHandler(ABC):
    def __init__(self, channel, msg: bytes, db, logger):
        self._data = json.loads(msg.decode())
        self._db = db
        self._channel = channel
        self._logger = logger
        self._post_init()

    @staticmethod
    def get_prefetch_count() -> int:
        return 10

    @classmethod
    @abstractmethod
    def get_handlers(cls) -> dict[str, Callable]:
        pass

    def _post_init(self):
        pass

    def _publish_message(self, exchange, route, message, *, persistent=True):
        self._channel.basic_publish(
            exchange,
            route,
            json.dumps(message).encode(),
            BasicProperties(delivery_mode=PERSISTENT_DELIVERY_MODE if persistent else TRANSIENT_DELIVERY_MODE),
        )
