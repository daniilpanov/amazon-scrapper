from pydantic import ValidationError
from .blackbox import BlackboxHandler
from .models import BlackboxDocument
from ..abstract_handler import AbstractHandler


class HeliumHandler(AbstractHandler):
    @classmethod
    def get_handlers(cls):
        return {
            "result.success.helium_blackbox": {"handler": cls.handle_success_helium_blackbox},
            "result.error.helium_blackbox": {"handler": cls.handle_error_helium_blackbox},
        }

    def handle_success_helium_blackbox(self, msg):
        validated = []
        errors = []
        for item in self._data:
            try:
                validated.append(BlackboxDocument(**item))
            except ValidationError as e:
                errors.append(e.errors())

        if validated:
            BlackboxHandler(self._logger).success(self._db, validated)

    def handle_error_helium_blackbox(self, msg):
        BlackboxHandler(self._logger).error(msg)


handler = HeliumHandler
