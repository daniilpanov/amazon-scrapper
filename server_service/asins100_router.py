from bson import ObjectId
from fastapi import APIRouter
from pydantic import BaseModel
from pymongo.errors import PyMongoError
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT, \
    HTTP_500_INTERNAL_SERVER_ERROR

import tasks_manager


class Get100AsinsResult(BaseModel):
    asins: list[str]


class Get100AsinsTask(BaseModel):
    alias: str | None = None
    label: str
    type: str
    limit: int = 100
    stage: int = 0


router = APIRouter(prefix='/helium')


@router.post('/get100asins')
async def get_100asins(config: Get100AsinsTask):
    data = tasks_manager.add_task(
        '100asins',
        {'alias': config.alias or config.type + ' ' + config.label + '#100asins'},
        [{'label': config.label, 'type': config.type, 'limit': config.limit}],
        stage=config.stage,
    )
    return Response(str(data[0]) + '--' + str(data[1][0]), status_code=HTTP_200_OK)


@router.get('/result_100asins/{task_id}')
async def get_helium_result(task_id: str):
    if '--' not in task_id:
        raise HTTPException(HTTP_400_BAD_REQUEST)
    header_id, body_id = task_id.split('--')
    task = tasks_manager.get_task(body_id)
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
        task = tasks_manager.get_task(task_id)
        data = {'result': result.asins}
        if stage := int(task.get('stage', 0)):
            data['stage'] = stage + 1
        res = tasks_manager.TasksBodies.update_one({'_id': task_id}, {'$set': data}).modified_count
    except PyMongoError as e:
        print(e)
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e
    if stage != 1:
        tasks_manager.finish_task(task_id, True)
    tasks_manager.release_task(task_id)
    return Response(str(res))
