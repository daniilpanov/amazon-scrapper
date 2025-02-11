import dns.resolver
dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
dns.resolver.default_resolver.nameservers=['8.8.8.8']

import logging
import uuid
import asyncio
from logging import FileHandler

from dotenv import load_dotenv

load_dotenv('.env') or load_dotenv('../.env')

import certifi
from os import environ as env
from pymongo import AsyncMongoClient
from pymongo.errors import BulkWriteError
from pymongo.server_api import ServerApi

# Create a logger object
logger = logging.getLogger(__name__)
# Set the logging level to INFO
logger.setLevel(logging.DEBUG)
# Create a handler that logs to the Docker logs
handler = FileHandler(filename='./transform-departments.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)


class Uploader:
    chunk: list
    chunk_size = 200
    coll = None
    lnk_coll = None
    cache = None

    def __init__(self, coll, lnk_coll):
        self.coll = coll
        self.lnk_coll = lnk_coll
        self.chunk = []

    async def flush(self):
        if not self.chunk:
            return self.chunk
        try:
            data = [dict(zip(('uuid', 'name', 'type', 'parent', 'level', 'url'), item.inst_data())) for item in
                    self.chunk]
            await self.coll.insert_many(data, ordered=False)
        except BulkWriteError as e:
            unique_data = list(i['keyValue'] for i in e.details['writeErrors'])
            async for i in self.coll.find({'$or': unique_data}):
                logger.debug('>' + str(i))
                for item in self.chunk:
                    if item.levels[-1] == i['name'] and len(item.levels) == i['level'] and item.parent == i['parent']:
                        logger.debug('changed!')
                        item.uuid = i['uuid']
                        break
        except Exception as e:
            logger.exception(str(e))
        finally:
            old = self.chunk
            self.chunk = []
            if not self.cache:
                return
            for item in old:
                logger.info('set to cache: ' + str(item.levels) + ' ' + item.uuid)
                self.cache[item.levels] = item.uuid

    async def load_data(self, item):
        if not item.parent and item.level:
            print(item.levels, item.uuid, item.url, item.target, item.items)
            logger.error(f"{item.levels} {item.uuid} {item.url} {item.target} {item.items}")
            print(self.cache.parent_list_uid if self.cache else None)
            logger.debug(str(self.cache.parent_list_uid if self.cache else None))
            raise Exception('No parent!')
        if item.items:
            logger.info('loading items: ' + item.uuid + str(item.levels[-1]))
            try:
                await self.lnk_coll.insert_many(
                    [{'product_id': i['asin'], 'category': item.uuid, 'bsr_number': i['number_in_BSR'], 'product_source': 'AMAZON'} for i in item.items],
                    ordered=False)
            except BulkWriteError as e:
                logger.exception(str(e))
        self.chunk.append(item)
        if len(self.chunk) >= self.chunk_size:
            return await self.flush()


class CacheUUID:
    parent_list_uid: dict

    def __init__(self):
        self.parent_list_uid = {}

    def __setitem__(self, levels, uid):
        self.parent_list_uid[tuple(levels)] = uid

    def __getitem__(self, levels):
        return self.parent_list_uid[tuple(levels)]

    def get(self, levels):
        return self.parent_list_uid.get(tuple(levels))


bsr_fields_map = [
    'Department',
    'Category',
    'Sub_category',
    'Sub_category_1',
    'Sub_category_2',
    'Sub_category_3',
    'Sub_category_4',
    'Sub_category_5',
    'Sub_category_6',
    'Sub_category_-',
]
bsr_types_map = [
    'Department',
    'Category',
    'Sub',
]


class Item:
    levels: tuple | None = None
    level: int | None = None
    parent: str | None = None
    type: str | None = None
    uuid: str | None = None
    url: str | None = None
    target = True
    items: list[dict] | None = None

    def inst_data(self):
        if self.uuid is None:
            return None
        return self.uuid, self.levels[-1], self.type, self.parent, len(self.levels) - 1, self.url

    def __hash__(self):
        return hash(self.inst_data()[1:])

    def __eq__(self, oth):
        return hash(self) == hash(oth)

    def __init__(self, item, level):
        ls = []  # levels
        end_level = False
        i = 0
        for i, k in enumerate(bsr_fields_map[:-1]):
            ls.append(item[k].strip())
            if item[bsr_fields_map[i + 1]] == 'NaN':
                end_level = True
                break
            if i >= level:
                break
        else:
            ls.append(item[bsr_fields_map[-1]].strip())
            end_level = True
        if end_level:
            if level > len(ls) - 1:
                self.target = False
                return
            self.items = item.get('items', [])
            url = item['URL']
            if url and url.count('/') > 1:
                url, ref = item['URL'].rsplit('/', maxsplit=1)
                url = url.lstrip('https://').lstrip('www.').lstrip('amazon.com')
                if not ref.startswith('ref'):
                    url += '/' + ref
                if not url.startswith('/'):
                    url = '/' + url
            if url:
                url = 'https://www.amazon.com' + url
            self.url = url or None
        self.level = level
        self.levels = tuple(ls)
        self.type = bsr_types_map[min(2, i)].upper()
        self.uuid = str(uuid.uuid4())


def find_parent(ri, cache):
    try:
        if ri.uuid:
            logger.info('get from cache: ' + ri.uuid + ' - ' + str(ri.levels) + ', parent: ' + str(cache.get(ri.levels[:-1])))
            ri.parent = cache.get(ri.levels[:-1])
    except Exception as e:
        logger.exception('Error: ' + str(e) + ' ' + str(type(e)) + ' ' + ri.uuid + ' ' + ri.level + ' ' + ri.url)
    finally:
        return ri


async def slice_parse_data(data, level, cache):
    _slice = set()
    async for item in data:
        item = find_parent(Item(item, level), cache)
        if not item.uuid or not item.target:
            continue
        if not item.parent and level:
            print(item.levels, item.uuid, item.url, item.target, item.items)
            logger.error(f"{item.levels} {item.uuid} {item.url} {item.target} {item.items}")
            print(cache.parent_list_uid)
            logger.debug(str(cache.parent_list_uid))
            raise Exception('No parent!')
        _slice.add(item)
    return _slice


async def main():
    url = f"{env.get('MONGO_DB_HOST_SCHEMA')}://{env.get('MONGO_DB_USER')}:{env.get('MONGO_DB_PASS')}@{env.get('MONGO_DB_HOST')}"

    async with AsyncMongoClient(url, server_api=ServerApi('1'), username=env.get('MONGO_DB_USER'),
                                password=env.get('MONGO_DB_PASS'), tlsCAFile=certifi.where()) as mc:
        coll = mc['ai_highlights']['departments']
        data = coll.find({'Sub_category_-': {'$exists': True}})
        upl = Uploader(mc['amazon_dev']['categories'], mc['amazon_dev']['products_categories'])
        cache = CacheUUID()
        upl.cache = cache
        logger.info('Start loading data...')
        for i, k in enumerate(bsr_fields_map):
            logger.info('Loading level: ' + str(i))
            _slice = await slice_parse_data(data.clone(), i, cache)
            for item in _slice:
                logger.info('item data: ' + str(item.inst_data()))
                await upl.load_data(item)
            await upl.flush()
        logger.info('finish')


asyncio.run(main())
