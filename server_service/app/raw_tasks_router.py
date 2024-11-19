import typing

from .helpers import orjson_response
from fastapi import APIRouter, HTTPException
import orjson
from pydantic import BaseModel
from starlette.responses import Response
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT, HTTP_200_OK

from . import tasks_manager

router = APIRouter(prefix='/tasks')


class ReportForm(BaseModel):
    confirm: bool = True
    errors: list
    stop: bool = False


class StageForm(BaseModel):
    release: bool = False
    stage: int = None
    result: typing.Any = None
    result_key: str | None = None


@router.delete('/delete/{header_id}')
async def delete_task_req(header_id: str, force_delete: bool = False):
    return Response(bytes(tasks_manager.remove_task(header_id, force_delete)))


@router.patch('/confirm/{task_id}')
async def confirm_task_status_req(task_id: str, confirm_status: int):
    return Response(bytes(tasks_manager.confirm_status(task_id, confirm_status)))


@router.patch('/stop/{task_id}')
async def stop_task_req(task_id: str):
    return Response(bytes(tasks_manager.stop_task(task_id)))


@router.patch('/finish/{task_id}')
async def finish_task_req(task_id: str, confirm: bool = True):
    return Response(bytes(tasks_manager.finish_task(task_id, confirm)))


@router.patch('/report/{task_id}')
async def report_task_req(task_id: str, error: ReportForm):
    return Response(bytes(tasks_manager.report_task(task_id, error.errors, error.confirm, error.stop)))


@router.patch('/stage/{task_id}')
async def set_task_stage_req(task_id: str, stage: StageForm):
    if not (stage.stage or (stage.result or stage.result is None)):
        raise HTTPException(HTTP_400_BAD_REQUEST)
    params = (({
                   'stage': stage.stage,
               } if stage.stage else {'stage': 0}) | (({
        ('result.' + stage.result_key if stage.result_key else 'result'): stage.result,
    }) if stage.result else {}))
    return Response(bytes(tasks_manager.set_task_stage(task_id, release=stage.release, **params)))


@router.get('/get/{task_id}')
async def get_task_req(task_id: str, with_header: bool = True, body_only: bool = False):
    data = tasks_manager.get_task(task_id, with_header)
    if body_only:
        data = data['result']
    return orjson_response(data)


@router.get('/get')
async def get_tasks_req(script: str | None = None, visible: bool | None = None, with_result: bool = False):
    res = list(tasks_manager.get_all_tasks(
        ({'script': script} if script else {}) | ({} if visible is None else {'taskHeader.visible': visible}),
        {} if with_result else {'result': 0},
    ))
    return orjson_response(res)


@router.get('/get_groups')
async def get_tasks_req(script: str | None = None, visible: bool | None = None):
    res = list(tasks_manager.get_tasks_groups(
        {'script': script} if script else {},
        visible,
    ))
    return orjson_response(res)


@router.get('/filter')
async def filter_tasks_req(_filter: str):
    prepared_filter = orjson.loads(_filter)
    return orjson_response(tasks_manager.get_all_tasks(prepared_filter))


@router.post('/acquire/{script}/{header_id}/{task_id}')
async def acquire_task_req(script: str, header_id: str, task_id: str):
    res = tasks_manager.acquire_task(script, task_id, header_id)
    if not res:
        raise HTTPException(HTTP_409_CONFLICT)
    if res:
        tasks_manager.set_status(task_id, tasks_manager.TaskStatusEnum.started, True)
    return orjson_response(res)


@router.post('/release/{task_id}')
async def release_task_req(task_id: str):
    return Response(bytes(tasks_manager.release_task(task_id)), status_code=HTTP_200_OK)


@router.get('/get_available')
@router.get('/get_available/{script}')
@router.get('/get_available/{script}/{stage}')
async def get_available_tasks_req(script: str | None = None, stage: int = -1):
    _filters = ({'script': script} if script else {}) | {'status': {'$lt': tasks_manager.TaskStatusEnum.stopped},
                                                         'taskLock': {'$exists': False}} | (
                   {'stage': stage} if stage > -1 else {})
    res = list(tasks_manager.get_all_tasks(_filters, limit=20))
    return orjson_response(res)

