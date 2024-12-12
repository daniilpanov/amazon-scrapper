import logging
import os
from contextlib import asynccontextmanager
from logging.handlers import TimedRotatingFileHandler

import certifi
from bson import ObjectId
from fastapi import FastAPI, APIRouter, HTTPException
from pymongo import AsyncMongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.server_api import ServerApi
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_404_NOT_FOUND

from .fastapi_models import InfoBSRForm, ASINsBSRForm


# Create a logger object
logger = logging.getLogger(__name__)
# Set the logging level to INFO
logger.setLevel(logging.DEBUG)
# Create a handler that logs to the Docker logs
handler = TimedRotatingFileHandler(when='h', backupCount=2, utc=True, filename='logs/bsrloader.log')
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

db_global_prefix = os.environ.get('DB_GLOBAL_PREFIX', '')
collections_global_prefix = os.environ.get('COLLECTIONS_GLOBAL_PREFIX', '')
db: AsyncMongoClient | None = None


def collection(name, schema):
    return db[db_global_prefix + schema][collections_global_prefix + name]


@asynccontextmanager
async def lifespan(_: FastAPI):
    global db
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
    db = AsyncMongoClient(url, server_api=ServerApi('1'), username=username, password=password, tlsCAFile=certifi.where())
    yield
    await db.close()


app = FastAPI(lifespan=lifespan)
router = APIRouter(prefix='/v1/bsr')


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


@router.post('/load/bsr')
async def load_bsr_info(info: InfoBSRForm):
    data = dict.fromkeys(bsr_fields_map, 'NaN')
    i = 0
    for i, (key, val) in enumerate(info.departments_flat_tree.items()):
        data[bsr_fields_map[i]] = key
    if not i:
        raise HTTPException(HTTP_400_BAD_REQUEST)
    data['URL'], data['ref'] = info.departments_flat_tree[key].rsplit('/', maxsplit=1)
    if not data['ref'].startswith('ref'):
        data['URL'] += '/' + data['ref']
        data['ref'] = None
    try:
        res = await collection('departments', 'ai_highlights').insert_one(data)
        return JSONResponse({
            'bsr_id': str(res.inserted_id),
        })
    except DuplicateKeyError:
        del data['ref']
        del data['_id']
        res = await collection('departments', 'ai_highlights').find_one(data)
        return JSONResponse({
            'bsr_id': str(res['_id']),
        })
    except PyMongoError as e:
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e


@router.post('/load/asins')
async def load_bsr_asins(data: ASINsBSRForm):
    res = await collection('departments', 'ai_highlights').find_one({'_id': ObjectId(data.bsr_id)})
    if not res:
        raise HTTPException(HTTP_404_NOT_FOUND)
    new_items = data.model_dump(include={'asins'})['asins']
    res['items'] = res.get('items', [])

    for i in range(len(new_items)):
        asin_new_data = new_items[i]
        if not asin_new_data.get('asin'):
            continue
        if not all([asin_new_data.get('title'), asin_new_data.get('image'), asin_new_data.get('score'), asin_new_data.get('number_in_BSR')]):
            for j in range(len(res['items'])):
                asin_exist_data = res['items'][j]
                if asin_new_data['asin'] != asin_exist_data['asin']:
                    continue
                asin_new_data = asin_exist_data | asin_new_data
        new_items[i] = asin_new_data

    try:
        await collection('departments', 'ai_highlights').update_one({'_id': ObjectId(data.bsr_id)}, {'$set': {'items': new_items}})
        return JSONResponse({
            'bsr_url': res['URL'],
            'bsr_id': str(res['_id']),
            'nodata_asins': list(map(lambda item: item['asin'], filter(lambda item: not all([item.get('title'), item.get('score'), item.get('image')]), new_items)))
        })
    except PyMongoError as e:
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e


app.include_router(router)
