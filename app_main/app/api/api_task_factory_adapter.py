from fastapi import Response
from pydantic import BaseModel

from .abstract_api import AbstractAPI
from ..task_factories.amazon_zip import AmazonZipFactory
from ..task_factories.asinsight import AsinSightFactory
from ..task_factories.helium_blackbox import HeliumBlackBoxFactory
from ..task_factories.keyword_tracker import KeywordTrackerFactory


class HeliumBlackBoxTaskInput(BaseModel):
    user_id: int
    max_cat_level: int


class AmazonZipTaskInput(BaseModel):
    zip_code: int


class TaskFactoryAdapterAPI(AbstractAPI):
    @staticmethod
    def get_prefix() -> str:
        return "/tasks"

    @staticmethod
    def get_tags() -> list[str]:
        return ["tasks"]

    def _add_task_start_route(self, path: str, method):
        self._router.add_api_route(path, method, methods=["POST"], status_code=204, response_class=Response)

    def _add_api_routes(self):
        self._add_task_start_route("/helium-blackbox", self.publish_helium_blackbox)
        self._add_task_start_route("/asinsight", self.publish_asinsight)
        self._add_task_start_route("/keyword-tracker", self.publish_keyword_tracker)
        self._add_task_start_route("/amazon-zip", self.publish_amazon_zip)

    def publish_asinsight(self):
        AsinSightFactory(self._db, self._channel).publish_asinsight_tasks()

    def publish_helium_blackbox(self, data_input: HeliumBlackBoxTaskInput):
        HeliumBlackBoxFactory(self._db, self._channel).publish_helium_blackbox(data_input.user_id, data_input.max_cat_level)

    def publish_keyword_tracker(self):
        KeywordTrackerFactory(self._db, self._channel).publish_keyword_tracker()

    def publish_amazon_zip(self, data_input: AmazonZipTaskInput):
        AmazonZipFactory(self._db, self._channel).publish_amazon_zip_task(data_input.zip_code)


router_class = TaskFactoryAdapterAPI
