import certifi
from pymongo.errors import BulkWriteError, PyMongoError

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from .models import *


class DBController:
    db_inst: MongoClient
    db_key = 'kalodata'

    def __init__(self, db_conf: dict):
        url = db_conf.get('url_prefix', '') + '://'
        if username := db_conf.get('username'):
            url += username
        if password := db_conf.get('password'):
            url += ':' + password
        if username or password:
            url += '@'
        url += db_conf.get('url', '')
        self.db_inst = MongoClient(
            url,
            server_api=ServerApi('1'),
            username=username,
            password=password,
            tlsCAFile=certifi.where(),
        )

    def add_shop(self, shp: Shop):
        try:
            return self.db_inst[self.db_key]['shops'].insert_one(shp.model_dump()).inserted_id
        except BulkWriteError:
            return None
        except PyMongoError:
            return False

    def add_product(self, prod: Product):
        try:
            creators_ids = prod.creators_ids
            res = self.db_inst[self.db_key]['products'].insert_one(prod.model_dump(exclude={'creators_ids'}))
            self.db_inst[self.db_key]['_products_creators_link'].insert_many(tuple({
                'creator_id': creator_id,
                'product_id': prod.internal_id,
            } for creator_id in creators_ids))
            return res.inserted_id
        except BulkWriteError:
            return None
        except PyMongoError:
            return False

    def add_creator(self, crea: Creator):
        try:
            shops_ids = crea.shops_ids
            products_ids = crea.products_ids
            res = self.db_inst[self.db_key]['creators'].insert_one(crea.model_dump(exclude={'products_ids', 'shops_ids'}))
            self.db_inst[self.db_key]['_products_creators_link'].insert_many(tuple({
                'creator_id': crea.internal_id,
                'product_id': product_id,
            } for product_id in products_ids))
            self.db_inst[self.db_key]['_shops_creators_link'].insert_many(tuple({
                'creator_id': crea.internal_id,
                'shop_id': shop_id,
            } for shop_id in shops_ids))
            return res.inserted_id
        except BulkWriteError:
            return None
        except PyMongoError:
            return False

    def add_video(self, vid: Video):
        try:
            return self.db_inst[self.db_key]['video_ad'].insert_one(vid.model_dump()).inserted_id
        except BulkWriteError:
            return None
        except PyMongoError:
            return False
