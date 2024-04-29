import datetime
import enum

import pymongo
import pytz
from bson import ObjectId

import database


class TaskStatusEnum(enum.IntEnum):
    created = 0
    started = 1
    stopped = 2
    finished = 3
    critical_error = -1


class StatusNotConfirmedError(Exception):
    pass


class CachedTaskView:
    # static
    lifetime = datetime.timedelta(minutes=120)
    # self
    data: dict
    created: datetime.datetime

    def __init__(self, data):
        global tasks_views_cache
        self.data = data
        self.created = datetime.datetime.now(pytz.UTC)
        tasks_views_cache[data['_id']] = self
        expired = []
        for tv_id, tv in tasks_views_cache.items():
            if datetime.datetime.now(pytz.UTC) - self.created > tv.lifetime:
                expired.append(tv_id)
        for tv_id in expired:
            del tasks_views_cache[tv_id]


tasks_views_cache: dict[str | ObjectId, CachedTaskView] = {}
TasksViews = database.db('amazon_scraper_features')['tasks_views']
Tasks = database.db('amazon_scraper_features')['tasks']
TasksLock = database.db('amazon_scraper_features')['tasks_lock']


def get_task_view(task_view_id):
    task_view_id = ObjectId(task_view_id)
    return tasks_views_cache.get(task_view_id, CachedTaskView(TasksViews.find_one({'_id': task_view_id}))).data


def add_task(script, alias=None, data=None, params=None):
    print(script, alias, data)
    keys = params.keys()
    all_params = len(params[keys[0]])
    r = TasksViews.insert_one({
        'script': script,
        'alias': alias,
        'data': data,
        'errors': {},  # key -- variable param, value -- error body
        'all_items': all_params or 1,  # all quantity of subtasks
        'progress': 0,  # how many subtasks are ready
        'result': {},  # summary result
        'created_at': datetime.datetime.now(pytz.UTC),
        'started_at': None,
        'ended_at': None,
    })

    if keys:
        tasks = []
        for i in range(all_params):
            doc = {}
            for k in keys:
                doc[k] = params[k][i]
            doc = {
                'script': script,
                'view_id': r.inserted_id,
                'status': TaskStatusEnum.created,
                'confirm_status': TaskStatusEnum.created,
                'hidden': {},
                'created_at': datetime.datetime.now(pytz.UTC),
                'started_at': None,
                'ended_at': None,
                'params': doc,
            }
            tasks.append(doc)
        Tasks.insert_many(tasks)
    else:
        Tasks.insert_one({
            'script': script,
            'view_id': r.inserted_id,
            'status': TaskStatusEnum.created,
            'confirm_status': TaskStatusEnum.created,
            'hidden': {},
            'created_at': datetime.datetime.now(pytz.UTC),
            'started_at': None,
            'ended_at': None,
        })

    return r.inserted_id


def report_error(view_id, error):
    TasksViews.update_one({'_id': ObjectId(view_id)}, {'$push': {'errors': error}})


def report_errors(view_id, errors):
    TasksViews.update_one({'_id': ObjectId(view_id)}, {'$push': {'errors': {'$each': [errors]}}})


def get_task(_id) -> dict:
    return Tasks.find_one(ObjectId(_id))


def _filter(script: str, with_status: int | list | dict | tuple | None = None, locked: bool | None = None,
            view_id=None):
    filters = {'script': script}
    if with_status is not None:
        if type(with_status) is list:
            filters['status'] = {'$in': with_status}
        else:
            filters['status'] = with_status
    if locked is not None:
        locks = list(ObjectId(task['task_id']) for task in TasksLock.find())
        filters['_id'] = {'$in': locks} if locked else {'$nin': locks}
    if view_id is not None:
        filters['view_id'] = ObjectId(view_id)
    return filters


def get_one_task(script: str, with_status: int | list | dict | tuple | None = None, locked: bool | None = None,
                 view_id=None):
    return Tasks.find_one(_filter(script, with_status, locked, view_id))


def get_tasks(script: str, with_status: int | list | dict | tuple | None = None, locked: bool | None = None,
              view_id=None):
    return Tasks.find(_filter(script, with_status, locked, view_id))


def get_all():
    return Tasks.find()


def confirm_task(_id, status: int, sync: bool = False, timestamp_field: str | None = None):
    Tasks.update_one({'_id': ObjectId(_id)}, {'$set': {
        'confirm_status': status,
    } | (
        {'status': status} if sync else {}
    ) | (
        {timestamp_field: datetime.datetime.now(pytz.UTC)} if timestamp_field else {}
    )})


def stop_task(_id):
    data = Tasks.find_one(ObjectId(_id))
    if -1 < data['status'] < TaskStatusEnum.stopped:
        Tasks.update_one({'_id': ObjectId(_id)}, {'$set': {
            'status': TaskStatusEnum.stopped,
        }})
        release_task(_id)


def acquire_task(_id):
    try:
        TasksLock.insert_one({'task_id': _id})
        return True
    except pymongo.errors.DuplicateKeyError:
        return False


def release_task(_id):
    TasksLock.delete_one({'task_id': _id})


def delete_view(_id, force=False):
    data = get_task_view(_id)
    if not data:
        return True
    tasks = get_tasks(data['script'], view_id=_id)
    if not force:
        for task in tasks:
            if task.get('confirm_status') != task['status']:
                raise StatusNotConfirmedError
            if task['status'] < TaskStatusEnum.stopped and task['status'] != TaskStatusEnum.created:
                return False
    Tasks.delete_many({'view_id': ObjectId(_id)})
    TasksViews.delete_one({'_id': ObjectId(_id)})
    TasksLock.delete_one({'task_id': ObjectId(_id)})
    return True
