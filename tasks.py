import datetime
import enum

import pymongo
import pytz
from bson import ObjectId
from pymongo import mongo_client

import database


class TaskStatusEnum(enum.IntEnum):
    created = 0
    started = 1
    paused = 2
    stopped = 3
    finished = 4
    critical_error = -1


def add_task(script, alias=None, data=None):
    print(script, alias, data)
    database.db('amazon_scraper_features')['tasks'].insert_one({
        'script': script,
        'alias': alias,
        'data': data,
        'success': None,
        'status': TaskStatusEnum.created,
        'progress': None,
        'hidden': None,
        'result': None,
        'created_at': datetime.datetime.now(pytz.UTC),
        'started_at': None,
        'ended_at': None,
    })


def get_task(_id) -> dict:
    return database.db('amazon_scraper_features')['tasks'].find_one(ObjectId(_id))


def get_tasks(script: str, with_status: int | None = None, locked: bool | None = None):
    filters = {'script': script}
    if with_status is not None:
        filters['status'] = with_status
    if locked is None:
        locked = False
        locks = set()
    else:
        locks = {task['_id'] for task in database.db('amazon_scraper_features')['tasks_lock'].find()}
    return [task for task in database.db('amazon_scraper_features')['tasks'].find(filters) if (task['_id'] in locks) is locked]


def get_all():
    return database.db('amazon_scraper_features')['tasks'].find()


def stop_task(_id, pause=False):
    data = database.db('amazon_scraper_features')['tasks'].find_one(ObjectId(_id))
    if data['status'] < 2:
        database.db('amazon_scraper_features')['tasks'].update_one({'_id': ObjectId(_id)}, {'$set': {
            'status': 2 + (not pause),
        }})
        if not pause:
            release_task(_id)


def acquire_task(_id):
    try:
        database.db('amazon_scraper_features')['tasks_lock'].insert_one({'task_id': _id})
        return True
    except pymongo.errors.DuplicateKeyError:
        return False


def release_task(_id):
    database.db('amazon_scraper_features')['tasks_lock'].delete_one({'task_id': _id})
