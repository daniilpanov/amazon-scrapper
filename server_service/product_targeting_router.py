import datetime

import pytz
from bson import ObjectId
from fastapi import APIRouter
from pydantic import BaseModel
from pymongo.errors import PyMongoError, BulkWriteError, DuplicateKeyError
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT, \
    HTTP_500_INTERNAL_SERVER_ERROR

import db_mongo
import tasks_manager


class ProductTargetingQueryTask(BaseModel):
    alias: str | None = None
    query: str | None = None
    reference: str
    limit: int = 500


class ProductTargetingItemResult(BaseModel):
    query: str
    reference: str
    asin: str
    title: str
    description: str | None = None


router = APIRouter(prefix='/product-targeting')


# GET QUERY AND REFERENCE (1)
# START 100ASINS (2)
@router.post('/start')
async def start_product_target(config: ProductTargetingQueryTask):
    data = tasks_manager.add_task(
        'pt',
        {'alias': config.alias or config.query + '#PT-Query'},
        [{'query': config.query, 'limit': config.limit, 'reference': config.reference}],
    )
    return Response(str(data[0]) + '--' + str(data[1][0]), status_code=HTTP_200_OK)


@router.get('/result/{task_id}')
async def get_pt_query_result(task_id: str):
    if '--' not in task_id:
        raise HTTPException(HTTP_400_BAD_REQUEST)
    header_id, body_id = task_id.split('--')
    task = tasks_manager.get_task(body_id)
    if not task or task['status'] == tasks_manager.TaskStatusEnum.stopped or task['script'] != '100asins':
        raise HTTPException(HTTP_404_NOT_FOUND)
    return int(task['status'] >= tasks_manager.TaskStatusEnum.finished)


@router.post('/result/add')
async def load_result(item: ProductTargetingItemResult):
    data = {
        'reference': item.reference,
        'query': item.query,
        'asin': item.asin,
        'title': item.title,
        'description': item.description,
    }
    db_res = False
    try:
        db_res = db_mongo.db('amazon_data')['product_targeting'].insert_one(data).inserted_id
    except (BulkWriteError, DuplicateKeyError):
        pass
    except PyMongoError as e:
        print(e)
        tasks_manager.report_task(
            item.root_task_id,
            [datetime.datetime.now(pytz.UTC).isoformat() + ' [PT] ' + str(e)],
            stop=True,
            confirm=True,
        )
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e
    return Response(str(db_res))
