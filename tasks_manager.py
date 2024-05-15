import datetime
import enum

import pytz
from bson import ObjectId
from pymongo.errors import OperationFailure, PyMongoError, DuplicateKeyError

import database


class TaskStatusEnum(enum.IntEnum):
    created = 0
    started = 1
    stopped = 2
    finished = 3
    critical_error = 4


# Aggregations
TasksListView = database.db('scrap_process')['tasks_list_view']
TasksLockView = database.db('scrap_process')['tasks_lock_view']
TasksListLockView = database.db('scrap_process')['tasks_list_lock_view']
# Collections
TasksHeaders = database.db('scrap_process')['tasks_headers']
TasksBodies = database.db('scrap_process')['tasks_bodies']
TasksLock = database.db('scrap_process')['tasks_lock']


def add_task(script, view, data):
    if not data:
        return False
    res = TasksHeaders.insert_one({
        'script': script,
        'created_at': datetime.datetime.now(pytz.UTC),
        'started_at': None,
        'ended_at': None,
        **view,
    })
    nd_res = TasksBodies.insert_many(
        [{
            'script': script,
            'header_id': ObjectId(res.inserted_id),
            'data': datum,
            'status': TaskStatusEnum.created,
            'confirmed_status': TaskStatusEnum.created,
            'errors': {},  # key -- variable param, value -- error body
            'created_at': datetime.datetime.now(pytz.UTC),
            'started_at': None,
            'ended_at': None,
            'result': {},
        } for datum in data],
    )
    return res.inserted_id, nd_res.inserted_ids


def acquire_task(script, task_id, header_id):
    task_id = ObjectId(task_id)
    header_id = ObjectId(header_id)
    try:
        res = TasksLock.insert_one({'script': script, 'task_id': task_id, 'header_id': header_id})
        task_body = TasksBodies.find_one({'_id': task_id})
        if not task_body['started_at']:
            TasksBodies.update_one(
                {'_id': task_id},
                {'$set': {'started_at': datetime.datetime.now(pytz.UTC)}},
            )
        return res.inserted_id
    except DuplicateKeyError:
        return False
    except PyMongoError:
        # TODO: process error
        return False


def release_task(task_id):
    return TasksLock.delete_one({'task_id': ObjectId(task_id)}).deleted_count


def remove_task(header_id, force_delete=False):
    _id = ObjectId(header_id)
    if not force_delete:
        tasks = TasksListLockView.find({
            'header_id': _id,
            '$or': [
                {'taskLock': {'$exists': True}},
                {'status': {'$lte': TaskStatusEnum.started}},
                {'$expr': {'$ne': ['$status', '$confirmed_status']}}
            ],
        })
        try:
            # Есть активные задачи
            next(tasks)
            return False
        except StopIteration:
            pass

    try:
        res = TasksHeaders.delete_one({'_id': _id}).deleted_count
        res += TasksHeaders.delete_one({'_id': _id}).deleted_count
        res += TasksBodies.delete_many({'header_id': _id}).deleted_count
        return res
    except PyMongoError:
        # TODO: log
        return None


def stop_task(task_id, **params):
    task_id = ObjectId(task_id)
    return set_status(task_id, TaskStatusEnum.stopped, **params)


def finish_task(task_id, confirm=True, **params):
    task_id = ObjectId(task_id)
    return set_status(task_id, TaskStatusEnum.finished, confirm, ended_at=datetime.datetime.now(pytz.UTC), **params)


def set_status(task_id, status, confirmation=False, **params):
    task_id = ObjectId(task_id)
    return TasksBodies.update_one(
        {'_id': task_id},
        {'$set': ({'status': status} | ({'confirmed_status': status} if confirmation else {}) | params)},
    ).modified_count


def confirm_status(task_id, status, **params):
    task_id = ObjectId(task_id)
    return TasksBodies.update_one(
        {'_id': task_id},
        {'$set': {'confirmed_status': status} | params},
    ).modified_count


def get_task(task_id, with_header=False):
    task_id = ObjectId(task_id)
    try:
        if with_header:
            return TasksListView.find_one({'_id': task_id})
        return TasksBodies.find_one({'_id': task_id})
    except PyMongoError:
        raise


def get_one_task(_filters=None):
    try:
        return TasksListLockView.find_one(_filters or {})
    except OperationFailure:
        # TODO: log
        return False
    except PyMongoError:
        # TODO: log
        return None


def get_header(header_id, with_many_bodies=False):
    header_id = ObjectId(header_id)
    try:
        if with_many_bodies:
            return TasksListView.find_one({'header_id': header_id})
        return TasksHeaders.find_one({'_id': header_id})
    except OperationFailure:
        # TODO: log
        return None
    except PyMongoError:
        # TODO: log
        return None


def get_all_tasks(_filters=None):
    try:
        return TasksListLockView.find(_filters or {})
    except OperationFailure:
        # TODO: log
        return False
    except PyMongoError:
        # TODO: log
        return None
