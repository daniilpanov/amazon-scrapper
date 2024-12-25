import logging
import os
from contextlib import asynccontextmanager
from logging.handlers import TimedRotatingFileHandler
from urllib.parse import unquote

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
handler = TimedRotatingFileHandler(when='h', backupCount=2, utc=True, filename='logs/tiktokloader.log')
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
router = APIRouter(prefix='/v1/tiktok')





app.include_router(router)
