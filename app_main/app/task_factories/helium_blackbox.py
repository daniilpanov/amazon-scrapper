from .abstract_factory import AbstractFactory
from ..models.helium import HeliumBlackBoxTask


class HeliumBlackBoxFactory(AbstractFactory):
    def publish_helium_blackbox(self, user_id: int, level: int = 1):
        self._channel.basic_publish("tasks", "helium_blackbox", HeliumBlackBoxTask(
            maxCatLevel=level,
            userId=user_id,
        ))
