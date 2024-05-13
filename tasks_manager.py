import enum

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
    res = TasksHeaders.insert_one({
        'script': script,
        'status': TaskStatusEnum.created,
        'confirmed_status': TaskStatusEnum.created,
        **view,
    })
    nd_res = TasksBodies.insert_many(
        [{'script': script, 'header_id': ObjectId(res.inserted_id), 'data': datum} for datum in data],
    )
    return res.inserted_id, nd_res.inserted_ids


def acquire_task(script, task_id, header_id):
    task_id = ObjectId(task_id)
    header_id = ObjectId(header_id)
    try:
        res = TasksLock.insert_one({'script': script, 'task_id': task_id, 'header_id': header_id})
        return res.inserted_id
    except DuplicateKeyError:
        return False
    except PyMongoError:
        # TODO: process error
        return False


def release_task(task_id):
    return TasksLock.delete_one({'task_id': ObjectId(task_id)}).deleted_count


def remove_task(header_id):
    _id = ObjectId(header_id)
    tasks = TasksListLockView.find({
        'header_id': header_id,
        '$or': [
            {'taskLock': {'$exists': True}},
            {'status': {'$lte': TaskStatusEnum.started}},
            {'$expr': {'$ne': ['$status', '$confirmed_status']}}
        ],
    })
    try:
        next(tasks)
    except StopIteration:
        # Есть активные задачи
        return False

    try:
        TasksHeaders.delete_one({'_id': header_id})
        TasksBodies.delete_many({'header_id': header_id})
        TasksLock.delete_many({'header_id': header_id})
        return True
    except PyMongoError:
        raise


def stop_task(task_id):
    task_id = ObjectId(task_id)
    return set_status(task_id, TaskStatusEnum.stopped)


def set_status(task_id, status, confirmation=False):
    task_id = ObjectId(task_id)
    return TasksBodies.update_one(
        {'_id': task_id},
        {'$set': ({'status': status} | ({'confirmed_status': status} if confirmation else {}))},
    ).modified_count


def confirm_status(task_id, status):
    task_id = ObjectId(task_id)
    return TasksBodies.update_one(
        {'_id': task_id},
        {'$set': {'confirmed_status': status}},
    ).modified_count


def get_task(task_id, with_header=False):
    task_id = ObjectId(task_id)
    try:
        if with_header:
            return TasksListView.find_one({'_id': task_id})
        return TasksBodies.find_one({'_id': task_id})
    except:
        raise


def get_header(header_id, with_many_bodies=False):
    header_id = ObjectId(header_id)
    try:
        if with_many_bodies:
            return TasksListView.find_one({'header_id': header_id})
        return TasksHeaders.find_one({'_id': header_id})
    except:
        raise


def get_all_tasks(_filters=None):
    try:
        return TasksListLockView.find(_filters or {})
    except OperationFailure:
        # TODO: log
        pass
    except PyMongoError:
        # TODO: log
        return None
