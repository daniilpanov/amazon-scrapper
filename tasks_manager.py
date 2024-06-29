import datetime
import enum
from time import sleep

import pytz
from bson import ObjectId
from pymongo.errors import OperationFailure, PyMongoError, DuplicateKeyError

import db_mongo


acquired: set[ObjectId] = set()


class TaskStatusEnum(enum.IntEnum):
    created = 0
    started = 1
    stopped = 2
    finished = 3
    critical_error = 4


# Aggregations
TasksListView = db_mongo.db('scrap_process')['tasks_list_view']
TasksLockView = db_mongo.db('scrap_process')['tasks_lock_view']
TasksListLockView = db_mongo.db('scrap_process')['tasks_list_lock_view']
# Collections
TasksHeaders = db_mongo.db('scrap_process')['tasks_headers']
TasksBodies = db_mongo.db('scrap_process')['tasks_bodies']
TasksLock = db_mongo.db('scrap_process')['tasks_lock']


def add_task(script, view, data, visible: bool = True, stage=0):
    if not data:
        return False
    res = TasksHeaders.insert_one({
        'script': script,
        'visible': visible,
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
            'stage': stage,
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
    if task_id in acquired:
        return False
    header_id = ObjectId(header_id)
    try:
        res = TasksLock.insert_one({
            'script': script,
            'task_id': task_id,
            'header_id': header_id,
            'acquired_at': datetime.datetime.now(pytz.UTC),
        })
        task_body = TasksBodies.find_one({'_id': task_id})
        if not task_body['started_at']:
            TasksBodies.update_one(
                {'_id': task_id},
                {'$set': {'started_at': datetime.datetime.now(pytz.UTC)}},
            )
        acquired.add(task_id)
        return res.inserted_id
    except DuplicateKeyError:
        return False
    except PyMongoError:
        # TODO: process error
        return False


def release_task(task_id):
    task_id = ObjectId(task_id)
    try:
        acquired.remove(task_id)
    except KeyError:
        pass
    return TasksLock.delete_one({'task_id': task_id}).deleted_count


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


def report_task(task_id, errors, confirm=True, stop=False, **params):
    task_id = ObjectId(task_id)
    if confirm and 'ended_at' not in params:
        params['ended_at'] = datetime.datetime.now(pytz.UTC)
    if stop:
        res = set_status(task_id, TaskStatusEnum.critical_error, confirm, errors=errors, **params)
        release_task(task_id)
        return res
    return TasksBodies.update_one(
        {'_id': task_id},
        {'$push': {'errors': errors}} | params,
    ).modified_count


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


def set_task_stage(task_id, stage, release=False, **params):
    res1 = TasksBodies.update_one(
        {'_id': ObjectId(task_id)},
        {'$set': ({'stage': stage} | params)},
    ).modified_count
    res2 = release and release_task(task_id)
    return res1 and res2


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


def get_task_loop(func, script, delay=5000, ev=None, *, pre_func=None, post_func=None):
    task = None
    if pre_func:
        pre_func()
    try:
        while not ev or not ev.is_set():
            task = get_one_task({
                'script': script,
                'taskLock': {'$exists': False},
                'status': {'$lte': TaskStatusEnum.started},
                '$expr': {'$eq': ['$status', '$confirmed_status']},
            })
            if task:
                # Если не получается захватить задачу -- пропускаем
                if not acquire_task(script, task['_id'], task['taskHeader']['_id']):
                    task = None
                    continue
                # Если захватили -- запускаем функцию
                try:
                    func(task)
                # Ошибки логируем
                except Exception:
                    # TODO: log
                    pass
                # Отпускаем задачу
                release_task(task['_id'])
                task = None
            sleep(delay / 1000)
    except KeyboardInterrupt:
        if post_func:
            post_func(task)
        raise
