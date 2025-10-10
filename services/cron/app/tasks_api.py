import datetime

import pytz
from bson import ObjectId
from pymongo import MongoClient


class TasksGroup:
    conn: MongoClient
    group_id: None | ObjectId = None
    tasks: list[dict]

    task_data_options: dict
    script: str
    stage: int
    dt: datetime.datetime

    def __init__(self, conn: MongoClient, script, stage=0, **kwargs):
        self.conn = conn
        self.script = script
        self.stage = stage
        self.task_data_options = kwargs
        self.dt = datetime.datetime.now(pytz.UTC)
        self.tasks = []

    def create_group(self, alias = None):
        res = self.conn['scrap_process']['tasks_headers'].insert_one({
            'script': self.script,
            'visible': True,
            'created_at': self.dt,
            'started_at': None,
            'ended_at': None,
            'alias': alias or f'{self.script}.daily({self.dt.isoformat()})',
        })
        self.group_id = res.inserted_id
        return self.group_id

    def add_task(self, **params):
        task = {
            'script': self.script,
            'header_id': self.group_id,
            'data': self.task_data_options | params,
            'status': 2,
            'confirmed_status': 2,
            'stage': self.stage,
            'errors': [],
            'created_at': self.dt,
            'started_at': None,
            'ended_at': None,
            'result': {},
        }
        self.tasks.append(task)

    def update_tasks_header_id(self):
        tasks = []
        for task in self.tasks:
            task['header_id'] = self.group_id
            tasks.append(task)
        self.tasks = tasks

    def submit_tasks(self):
        self.update_tasks_header_id()
        res = self.conn['scrap_process']['tasks_bodies'].insert_many(self.tasks)
        return res.inserted_ids
