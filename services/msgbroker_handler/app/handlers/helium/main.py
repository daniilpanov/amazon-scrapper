import json

from pydantic import ValidationError
from .blackbox import BlackboxHandler
from .models import BlackboxDocument
from ..abstract_handler import AbstractHandler


class HeliumHandler(AbstractHandler):
    @property
    def handlers(self):
        return {
            'result.success.helium_blackbox': {'handler': self.handle_success_helium_blackbox},
            'result.error.helium_blackbox': {'handler': self.handle_error_helium_blackbox},
        }

    def handle_success_helium_blackbox(self, msg):
        try:
            data = json.loads(msg.decode())
        except json.decoder.JSONDecodeError:
            raise ValueError('Invalid JSON!')

        validated = []
        errors = []
        for item in data:
            try:
                validated.append(BlackboxDocument(**item))
            except ValidationError as e:
                errors.append(e.errors())

        if validated:
            BlackboxHandler(self._logger).success(self._db, validated)

    def handle_error_helium_blackbox(self, msg):
        BlackboxHandler(self._logger).error(msg)


handler = HeliumHandler
