import datetime
import enum

import pymongo
import pytz
from bson import ObjectId

import database


class TaskStatusEnum(enum.IntEnum):
    created = 0
    started = 1
    paused = 2
    stopped = 3
    finished = 4
    critical_error = -1


Tasks = database.db('amazon_scraper_features')['tasks']
TasksLock = database.db('amazon_scraper_features')['tasks_lock']


class StatusNotConfirmedError(Exception):
    pass


def add_task(script, alias=None, data=None):
    print(script, alias, data)
    Tasks.insert_one({
        'script': script,
        'alias': alias,
        'data': data,
        'success': None,
        'errors': [],
        'status': TaskStatusEnum.created,
        'confirm_status': None,
        'progress': None,
        'hidden': None,
        'result': None,
        'created_at': datetime.datetime.now(pytz.UTC),
        'started_at': None,
        'ended_at': None,
    })


def get_task(_id) -> dict:
    return Tasks.find_one(ObjectId(_id))


def get_tasks(script: str, with_status: int | None = None, locked: bool | None = None):
    filters = {'script': script}
    if with_status is not None:
        filters['status'] = with_status
    if locked is None:
        locked = False
        locks = set()
    else:
        locks = {task['_id'] for task in TasksLock.find()}
    return [task for task in Tasks.find(filters) if
            (task['_id'] in locks) is locked]


def get_all():
    return Tasks.find()


def stop_task(_id, pause=False):
    data = Tasks.find_one(ObjectId(_id))
    if -1 < data['status'] < 2 + (not pause):
        Tasks.update_one({'_id': ObjectId(_id)}, {'$set': {
            'status': 2 + (not pause),
        }})
        if not pause:
            release_task(_id)


def acquire_task(_id):
    try:
        TasksLock.insert_one({'task_id': _id})
        return True
    except pymongo.errors.DuplicateKeyError:
        return False


def release_task(_id):
    TasksLock.delete_one({'task_id': _id})


def delete_task(_id):
    data = get_task(_id)
    if not data:
        return True
    created_right_now = data.get('confirm_status') is None or data['status'] == 0
    if data.get('confirm_status') != data['status'] and not created_right_now:
        raise StatusNotConfirmedError
    if data['status'] > 2 or created_right_now:
        Tasks.delete_one({'_id': ObjectId(_id)})
        TasksLock.delete_one({'task_id': ObjectId(_id)})
        return True
    return False
