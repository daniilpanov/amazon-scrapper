import datetime

import certifi
import pytz

from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.server_api import ServerApi

if not load_dotenv('.env'):
    load_dotenv('../.env')

from os import environ as env


def main(db, alias='Test #1'):
    header = {
        "script": "100asins",
        "visible": True,
        "created_at": datetime.datetime.now(pytz.UTC),
        "started_at": None,
        "ended_at": None,
        "alias": alias,
    }

    body_template = {
        "header_id": None,
        "script": "100asins",
        "data": None,
        "status": 0,
        "confirmed_status": 0,
        "stage": 1,
        "errors": [],
        "created_at": datetime.datetime.now(pytz.UTC),
        "started_at": None,
        "ended_at": None,
        "result": [],
    }

    body_data_template = {
        "label": None,
        "type": "",
        "limit": "10",
        "domain": "amazon.com",
    }

    header_insert_res = db['scrap_process']['tasks_headers'].insert_one(header)
    body_template["header_id"] = header_insert_res.inserted_id
    bodies = []

    with open('kw-data.txt') as f:
        for line in f:
            tmp_body = body_template.copy()
            tmp_data = body_data_template.copy()
            tmp_data['label'] = line.strip()
            tmp_body['data'] = tmp_data
            bodies.append(tmp_body)
    db['scrap_process']['tasks_bodies'].insert_many(bodies)


url = f"{env.get('MONGO_DB_HOST_SCHEMA')}://{env.get('MONGO_DB_USER')}:{env.get('MONGO_DB_PASS')}@{env.get('MONGO_DB_HOST')}"
with MongoClient(url, server_api=ServerApi('1'), username=env.get('MONGO_DB_USER'), password=env.get('MONGO_DB_PASS'), tlsCAFile=certifi.where()) as db_inst:
    main(db_inst, input('Enter the alias [Test #1] :') or 'Test #1')
