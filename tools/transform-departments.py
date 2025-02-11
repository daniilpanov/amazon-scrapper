# import dns.resolver
# dns.resolver.default_resolver=dns.resolver.Resolver(configure=False)
# dns.resolver.default_resolver.nameservers=['8.8.8.8']
from dotenv import load_dotenv
from pymongo.collection import Collection

load_dotenv('.env') or load_dotenv('../.env')
import os
import uuid
import asyncio
import certifi
from bson import ObjectId
from pymongo import AsyncMongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.server_api import ServerApi

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
url = os.environ.get('MONGO_DB_HOST_SCHEMA', 'mongodb') + '://'
username = None
password = None
if 'MONGO_DB_USER' in os.environ:
    username = os.environ['MONGO_DB_USER']
    url += username
    if 'MONGO_DB_PASS' in os.environ:
        password = os.environ['MONGO_DB_PASS']
        url += ':' + password
    url += '@'
url += os.environ.get('MONGO_DB_HOST', 'localhost')
coll: Collection | None = None
data = None
new_data = []
chunk_size = 200


async def flush():
    global new_data
    try:
        await coll.insert_many(new_data, ordered=False)
        new_data = []
    except DuplicateKeyError:
        pass


def load_data(item):
    if len(new_data) >= chunk_size:
        return flush()
    new_data.append(item)


async def get_by_chunk():
    pass



async def recursive_getting(level: int, parent_levels: list[str], parent_UID: str | None = None):
    if level > 1:
        return
    levels_filter = {}
    for i, l in enumerate(bsr_fields_map):
        if i < level:
            levels_filter[l] = parent_levels[i]
        elif i > level:
            levels_filter[l] = 'NaN'
    items = coll.find(levels_filter, {'items': 0})
    async for it in items:
        url, ref = it['URL'].rsplit('/', maxsplit=1)
        url = url.lstrip('https://').lstrip('www.').lstrip('amazon.com')
        if not ref.startswith('ref'):
            url += '/' + ref
        uid = str(uuid.uuid4())
        new_data.append(i:={
            "uuid": uid,
            "name": it[bsr_fields_map[level]],
            "parent": parent_UID,
            "type": bsr_types_map[level] if level < len(bsr_types_map) else bsr_types_map[-1],
            "level": level,
            "url": url,
        })
        plist = [*parent_levels, it[bsr_fields_map[level]]]
        await recursive_getting(level + 1, plist, uid)


async def main():
    global coll
    global data
    async with AsyncMongoClient(url, server_api=ServerApi('1'), username=username, password=password, tlsCAFile=certifi.where()) as mc:
        coll = mc['ai_highlights']['departments']
        # data = coll.find({}, {'items': 0})
        await recursive_getting(0, [])
        print(new_data)
        # print(1, await coll.distinct('Department', {'Department': 1}))


asyncio.run(main())
