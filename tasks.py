import importlib
from concurrent.futures import ThreadPoolExecutor
from threading import Event
from typing import Any

import settings

tasks_threads = ThreadPoolExecutor(settings.THREADS['all'])
all_tasks = {}
current_id = 0


class Task:
    id: int
    progress: int = 0  # from 0 to 100
    all: int  # max_count
    success: bool | None = None
    script: str
    data: dict | list | None = None
    alias: str | None = None
    ev: Event
    result: Any | None = None

    def __init__(self, _id, script, data=None, alias=None):
        self.id = _id
        self.script = script
        self.data = data
        self.alias = alias
        self.ev = Event()

    def to_dict(self):
        return {
            'id': self.id, 'progress': self.progress,
            'alias': self.alias, 'data': self.data,
            'success': self.success, 'result': self.result,
        }

    def add_progress(self, value: int):
        self.progress += value / self.all * 100


def add_task(script, alias=None, data=None):
    print(script, alias, data)
    global current_id
    try:
        _id = current_id
        current_id += 1
        all_tasks[_id] = Task(_id, script, data, alias)
        if type(data) is list:
            tasks_threads.submit(importlib.import_module(script).run, ev=all_tasks[_id].ev, _id=_id, *data)
        elif type(data) is dict:
            tasks_threads.submit(importlib.import_module(script).run, ev=all_tasks[_id].ev, _id=_id, **data)
        else:
            tasks_threads.submit(importlib.import_module(script).run, ev=all_tasks[_id].ev, _id=_id)
        return _id
    except (ModuleNotFoundError, AttributeError):
        print(script)
        raise
        return False


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
