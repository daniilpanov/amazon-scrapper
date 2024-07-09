from bson import ObjectId
from fastapi import APIRouter
from pydantic import BaseModel
from pymongo.errors import PyMongoError
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT, \
    HTTP_500_INTERNAL_SERVER_ERROR

import tasks_manager

router = APIRouter(prefix='/helium')


class HeliumResult(BaseModel):
    image_urls: dict[str, str]
    titles: dict[str, str]
    export: str


class Get100AsinsResult(BaseModel):
    asins: list[str]


class HeliumAdditionalResult(BaseModel):
    characteristics: dict[str, str] | None
    about: list[str] | None
    variant: dict[str, str] | None
    aplus: str | None
    manufacturer: str | None


class HeliumAdditional2Result(BaseModel):
    title: str | None
    description: str | None


class HeliumTask(BaseModel):
    alias: str | None = None
    asins: tuple[str, ...]


class Get100AsinsTask(BaseModel):
    alias: str | None = None
    label: str
    type: str


# H10
@router.post('/get')
async def get_helium(config: HeliumTask):
    data = tasks_manager.add_task('h10', {'alias': config.alias or ','.join(config.asins) + '#h10'}, [{'asins': config.asins}]),
    return Response(str(data[0][0]) + '--' + str(data[0][1][0]), status_code=HTTP_200_OK)


@router.get('/result/{helium_id}')
async def get_helium_result(helium_id: str):
    if '--' not in helium_id:
        raise HTTPException(HTTP_400_BAD_REQUEST)
    header_id, body_id = helium_id.split('--')
    task = tasks_manager.get_task(body_id, True)
    if not task or task['status'] == tasks_manager.TaskStatusEnum.stopped:
        raise HTTPException(HTTP_404_NOT_FOUND)
    if task['status'] < tasks_manager.TaskStatusEnum.finished:
        return Response(status_code=HTTP_204_NO_CONTENT)
    if task['status'] == tasks_manager.TaskStatusEnum.critical_error:
        return {'errors': task['errors']}
    return task['result']


@router.post('/set/{helium_id}')
async def set_helium_result(helium_id: str, result: HeliumResult):
    helium_id = ObjectId(helium_id)
    try:
        res = tasks_manager.TasksBodies.update_one({'_id': helium_id}, {'$set': {'result.helium_data': {
            'titles': result.titles, 'image_urls': result.image_urls, 'csv_data': result.export,
        }}}).modified_count
    except PyMongoError as e:
        print(e)
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e
    task = tasks_manager.get_task(helium_id)
    if 'amazon_data' in task['result']:
        tasks_manager.finish_task(helium_id, True)
        tasks_manager.release_task(helium_id)
    return Response(str(res))


@router.post('/set/{helium_id}/amazon')
async def set_helium_amazon_result(helium_id: str, result: HeliumAdditionalResult):
    helium_id = ObjectId(helium_id)
    try:
        res = tasks_manager.TasksBodies.update_one({'_id': helium_id}, {'$set': {'result.amazon_data.other': {
            'characteristics': result.characteristics,
            'about': result.about,
            'variant': result.variant,
            'manufacturer': result.manufacturer,
            'aplus': result.aplus,
        }}}).modified_count
    except PyMongoError as e:
        print(e)
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e
    task = tasks_manager.get_task(helium_id)
    if 'helium_data' in task['result']:
        tasks_manager.finish_task(helium_id, True)
        tasks_manager.release_task(helium_id)
    return Response(str(res))


@router.post('/set/{helium_id}/amazon_target')
async def set_helium_amazon_result(helium_id: str, result: HeliumAdditional2Result):
    helium_id = ObjectId(helium_id)
    try:
        res = tasks_manager.TasksBodies.update_one({'_id': helium_id}, {'$set': {'result.amazon_data.target': {
            'title': result.title,
            'description': result.description,
        }}}).modified_count
    except PyMongoError as e:
        print(e)
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e
    task = tasks_manager.get_task(helium_id)
    if 'helium_data' in task['result']:
        tasks_manager.finish_task(helium_id, True)
        tasks_manager.release_task(helium_id)
    return Response(str(res))


# 100 ASINS
@router.post('/get100asins')
async def get_100asins(config: Get100AsinsTask):
    data = tasks_manager.add_task('100asins', {'alias': config.alias or config.type + ' ' + config.label + '#100asins'}, [{'label': config.label, 'type': config.type}]),
    return Response(str(data[0][0]) + '--' + str(data[0][1][0]), status_code=HTTP_200_OK)


@router.get('/result_100asins/{task_id}')
async def get_helium_result(task_id: str):
    if '--' not in task_id:
        raise HTTPException(HTTP_400_BAD_REQUEST)
    header_id, body_id = task_id.split('--')
    task = tasks_manager.get_task(body_id, True)
    if not task or task['status'] == tasks_manager.TaskStatusEnum.stopped:
        raise HTTPException(HTTP_404_NOT_FOUND)
    if task['status'] < tasks_manager.TaskStatusEnum.finished:
        return Response(status_code=HTTP_204_NO_CONTENT)
    if task['status'] == tasks_manager.TaskStatusEnum.critical_error:
        return {'errors': task['errors']}
    return task['result']


@router.post('/set_100asins/{task_id}')
async def set_100asins_result(task_id: str, result: Get100AsinsResult):
    task_id = ObjectId(task_id)
    try:
        res = tasks_manager.TasksBodies.update_one({'_id': task_id}, {'$set': {'result': result.asins}}).modified_count
    except PyMongoError as e:
        print(e)
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e
    tasks_manager.finish_task(task_id, True)
    tasks_manager.release_task(task_id)
    return Response(str(res))
