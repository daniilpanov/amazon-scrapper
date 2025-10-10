import datetime
import time

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, BulkWriteError

from .models import BlackboxDocument


class BlackboxHandler:
    def __init__(self, logger):
        self.logger = logger

    def success(self, db: MongoClient, data: list[BlackboxDocument]):
        try:
            db['Keywords']['helium_blackbox'].insert_many(
                [model.model_dump() | {
                    'ts_created': time.time(),
                    'date_key': datetime.datetime.combine(datetime.date.today(), datetime.time()),
                } for model in data],
                ordered=False,
            )
        except (DuplicateKeyError, BulkWriteError) as e:
            self.logger.exception(e)

    def error(self, msg):
        self.logger.error(msg)
