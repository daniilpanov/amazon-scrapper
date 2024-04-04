import asyncio
import datetime
import importlib
from asyncio import Queue
from threading import Event, Thread
from typing import Any

import pytz

import settings

all_tasks = {}
current_id = 0
active_tasks = {
    'collect_reviews': [],
    'collect_products': [],
    'collect_departments': [],
}


class Task:
    id: int
    progress: float = 0  # from 0 to 100
    all: int  # max_count
    success: bool | None = None
    script: str
    data: dict | list | None = None
    alias: str | None = None
    ev: Event
    result: Any | None = None
    started_at: datetime.datetime
    ended_at: datetime.datetime | None = None
    _progress_value: int = 0

    def __init__(self, _id, script, data=None, alias=None):
        self.id = _id
        self.script = script
        self.data = data
        self.alias = alias
        self.ev = Event()
        self.started_at = datetime.datetime.now(pytz.UTC)

    def to_dict(self):
        return {
            'id': self.id, 'progress': self.progress, 'script': self.script,
            'alias': self.alias, 'data': self.data, 'started_at': self.started_at.isoformat(),
            'success': self.success, 'result': self.result,
        }

    def add_progress(self, value: int):
        self._progress_value += value
        self.progress = round(self._progress_value / self.all * 100, 2)
        if self._progress_value >= self.all:
            self.progress = 100
            self.ended_at = datetime.datetime.now(pytz.UTC)
            if self.success is None:
                self.success = True


def get_limit_for(task: Task):
    return settings.THREADS.get(task.script) or settings.THREADS.get('all')


async def get_task_from_q(q):
    i = 0
    while True:
        try:
            return q.get_nowait()
        except asyncio.QueueEmpty:
            pass
        await asyncio.sleep(i)
        i += 1
        if i > 100:
            i = 0


def remove_nonactive():
    not_active = []
    for scr_var in active_tasks:
        for i, task in enumerate(active_tasks[scr_var]):
            task: asyncio.Task
            if task.cancelled() or task.done():
                not_active.append((scr_var, i))
    for na in not_active[::-1]:
        active_tasks[na[0]].pop(na[1])


async def task_executor():
    try:
        task_object, coro = await get_task_from_q(task_executor_q)
        i = 0
        while coro:
            remove_nonactive()
            if len(active_tasks[task_object.script]) < get_limit_for(task_object):
                active_tasks[task_object.script].append(
                    asyncio.get_event_loop().create_task(coro)
                )
            else:
                task_executor_q.put_nowait((task_object, coro))
            await asyncio.sleep(i)
            i += 1
            if i > 100:
                i = 0
            task_object, coro = await get_task_from_q(task_executor_q)
    except Exception as e:
        print(e)
    i = 0
    while active_tasks:
        remove_nonactive()
        await asyncio.sleep(i)
        i += 1
        if i > 100:
            i = 0


task_executor_q = Queue()
task_executor_thr = Thread(target=lambda: asyncio.run(task_executor()))


def add_task(script, alias=None, data=None):
    print(script, alias, data)
    global current_id
    try:
        _id = current_id
        current_id += 1
        all_tasks[_id] = task_obj = Task(_id, script, data, alias)
        if type(data) is list:
            coroutines = importlib.import_module(script).get_runnable(ev=all_tasks[_id].ev, _id=_id, *data)
        elif type(data) is dict:
            coroutines = importlib.import_module(script).get_runnable(ev=all_tasks[_id].ev, _id=_id, **data)
        else:
            coroutines = importlib.import_module(script).get_runnable(ev=all_tasks[_id].ev, _id=_id)
        for coro in coroutines:
            task_executor_q.put_nowait((task_obj, coro))
        return _id
    except (ModuleNotFoundError, AttributeError):
        print(script)


def find_task(alias):
    return all_tasks.get(alias)


def get_task(_id) -> Task:
    return all_tasks[_id] if _id in all_tasks else None


def delete_task(_id):
    all_tasks[_id].ev.set()
    del all_tasks[_id]


def wait_task_nowait(_id):
    return all_tasks[_id] if all_tasks[_id].success is not None else None


def wait_task(_id):
    res = False
    while not res:
        res = wait_task_nowait(_id)
    return res
