import datetime

import pytz
from bson import ObjectId
from fastapi import APIRouter
from pydantic import BaseModel
from pymongo.errors import PyMongoError, BulkWriteError
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT, \
    HTTP_500_INTERNAL_SERVER_ERROR

import db_mongo
import tasks_manager


# 1
class ProductTargetingASINTask(BaseModel):
    alias: str | None = None
    reference_asin: str


class ProductTargetingASINResult(BaseModel):
    alias: str | None = None
    reference_asin: str
    query: str


# 2
class ProductTargetingQueryTask(BaseModel):
    alias: str | None = None
    query: str | None = None
    reference: str
    limit: int = 1000


# 3
class ProductTargetingItemTask(BaseModel):
    alias: str | None = None
    query: str | None = None
    reference: str
    asin: str
    root_task_id: str


class ProductTargetingItemResult(BaseModel):
    root_task_id: str
    query: str
    reference: str
    asin: str
    title: str
    description: str | None = None


router = APIRouter(prefix='/product-targeting')


# GET QUERY AND REFERENCE (1)
@router.post('/start/asin')
async def start_product_target(config: ProductTargetingASINTask):
    data = tasks_manager.add_task('PT-Ref', {
        'alias': config.alias,
    }, [{'reference_asin': config.reference_asin}])
    return Response(str(data[0]) + '--' + str(data[1][0]), status_code=HTTP_200_OK)


@router.get('/result/asin/{task_id}')
async def get_pt_asin_result(task_id: str):
    if '--' not in task_id:
        raise HTTPException(HTTP_400_BAD_REQUEST)
    header_id, body_id = task_id.split('--')
    task = tasks_manager.get_task(body_id)
    if not task or task['status'] == tasks_manager.TaskStatusEnum.stopped or task['script'] != 'PT-Ref':
        raise HTTPException(HTTP_404_NOT_FOUND)
    if task['status'] < tasks_manager.TaskStatusEnum.finished:
        return Response(status_code=HTTP_204_NO_CONTENT)
    if task['status'] == tasks_manager.TaskStatusEnum.critical_error:
        return {'errors': task['errors']}
    return task['result']


@router.post('/result/set/asin/{task_id}')
async def set_pt_asin_result(task_id: str, result: ProductTargetingASINResult):
    task_id = ObjectId(task_id)
    try:
        data = {'result': {'reference': result.reference_asin, 'query': result.query}}
        res = tasks_manager.TasksBodies.update_one({'_id': task_id}, {'$set': data}).modified_count
    except PyMongoError as e:
        print(e)
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e
    tasks_manager.finish_task(task_id, True)
    tasks_manager.release_task(task_id)
    return Response(str(res))


# START 100ASINS (2)
@router.post('/start/query')
async def start_product_target(config: ProductTargetingQueryTask):
    data = tasks_manager.add_task(
        '100asins',
        {'alias': config.alias or config.query + '#PT-Query'},
        [{'label': config.query, 'type': '', 'limit': config.limit, 'reference': config.reference}],
        stage=1,
    )
    return Response(str(data[0]) + '--' + str(data[1][0]), status_code=HTTP_200_OK)


@router.get('/result/query/{task_id}')
async def get_pt_query_result(task_id: str):
    if '--' not in task_id:
        raise HTTPException(HTTP_400_BAD_REQUEST)
    header_id, body_id = task_id.split('--')
    task = tasks_manager.get_task(body_id)
    if not task or task['status'] == tasks_manager.TaskStatusEnum.stopped or task['script'] != '100asins':
        raise HTTPException(HTTP_404_NOT_FOUND)
    return int(task['status'] >= tasks_manager.TaskStatusEnum.finished)


# GET ASIN INFO (3)
@router.post('/start/item')
async def start_product_item_target(config: ProductTargetingItemTask):
    data = tasks_manager.add_task('PT-Item', {
        'alias': config.alias,
    }, [{
        'root_task_id': config.root_task_id,
        'query': config.query or config.reference,
        'reference': config.reference,
        'asin': config.asin,
    }])
    return Response(str(data[0]) + '--' + str(data[1][0]), status_code=HTTP_200_OK)


@router.post('/result/set/item')
async def load_result(res: list[ProductTargetingItemResult]):
    data = [{
        'reference': item.reference,
        'query': item.query,
        'asin': item.asin,
        'title': item.title,
        'description': item.description,
    } for item in res]
    db_res = []
    try:
        db_res = db_mongo.db('amazon_data')['product_targeting'].insert_many(data, ordered=False).inserted_ids
    except BulkWriteError:
        pass
    except PyMongoError as e:
        print(e)
        tasks_manager.report_task(
            res[0].root_task_id,
            [datetime.datetime.now(pytz.UTC).isoformat() + ' [PT] ' + str(e)],
            stop=True,
            confirm=True,
        )
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e
    root_task_id = ObjectId(res[0].root_task_id)
    tasks_manager.TasksBodies.update_one({'_id': root_task_id}, {'$inc': {'asins_count': -1}})
    task = tasks_manager.get_task(root_task_id)
    if task and task.get('asins_count', 0) <= 0:
        tasks_manager.finish_task(root_task_id, confirm=True)
        tasks_manager.release_task(root_task_id)
    return Response(str(len(db_res)))

