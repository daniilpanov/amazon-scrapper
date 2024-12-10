import os

import certifi
from fastapi import FastAPI, APIRouter
from future.backports.http.client import HTTPException
from pymongo import AsyncMongoClient
from pymongo.errors import DuplicateKeyError, PyMongoError
from pymongo.server_api import ServerApi
from starlette.responses import JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

from services.amazon_departments_loader.app.fastapi_models import InfoBSRForm, ASINsBSRForm

db_global_prefix = os.environ.get('DB_GLOBAL_PREFIX', '')
collections_global_prefix = os.environ.get('COLLECTIONS_GLOBAL_PREFIX', '')
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


def collection(name, schema):
    return db[db_global_prefix + schema][collections_global_prefix + name]


app = FastAPI()
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
    data['URL'] = info.departments_flat_tree[key]
    try:
        res = await collection('departments', 'ai_highlights').insert_one(data)
        return JSONResponse({
            'bsr_id': str(res.inserted_id),
        })
    except DuplicateKeyError:
        res = await collection('departments', 'ai_highlights').find_one(data)
        return JSONResponse({
            'bsr_id': str(res['_id']),
        })
    except PyMongoError as e:
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e


@router.post('/load/asins')
async def load_bsr_asins(data: ASINsBSRForm):
    pass


app.include_router(router)
