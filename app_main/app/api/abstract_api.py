from abc import ABC, abstractmethod

from fastapi import APIRouter


class AbstractAPI(ABC):
    def __init__(self, db, channel, logger):
        self._initialized = False
        self._db = db
        self._channel = channel
        self._logger = logger
        self._router = APIRouter(prefix=self.get_prefix(), tags=self.get_tags())

    @staticmethod
    def get_prefix() -> str | None:
        return None

    @staticmethod
    def get_tags() -> list[str]:
        return []

    def _initialize_router(self):
        if self._initialized:
            return

        self._add_api_routes()
        self._initialized = True

    @abstractmethod
    def _add_api_routes(self):
        pass

    def get_router(self):
        self._initialize_router()
        return self._router
