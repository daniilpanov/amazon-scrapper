import importlib
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import settings

tasks_threads = ThreadPoolExecutor(settings.THREADS)
all_tasks = {}


class Task:
    id: int
    progress: int = 0  # from 0 to 100
    success: bool | None = None
    script: str
    data: dict | list | None = None
    alias: str | None = None
    ev: Event

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
            'success': self.success,
        }


def add_task(script, alias=None, data=None):
    try:
        _id = len(all_tasks)
        all_tasks[_id] = Task(_id, script, data, alias)
        if type(data) is list:
            tasks_threads.submit(importlib.import_module(script).run, all_tasks[_id].ev, *data)
        elif type(data) is dict:
            tasks_threads.submit(importlib.import_module(script).run, all_tasks[_id].ev, **data)
        return _id
    except (ModuleNotFoundError, AttributeError):
        return False


def get_task(_id):
    return all_tasks[_id].to_dict() if _id in all_tasks else None


def delete_task(_id):
    all_tasks[_id].ev.set()
    del all_tasks[_id]
