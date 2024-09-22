import datetime

import pymongo
import pytz

import db_mongo

priority_deps = list(db_mongo.db('ai_highlights')['departments'].find({'priority': {'$exists': True}}).sort('priority', pymongo.ASCENDING))
usual_deps = list(db_mongo.db('ai_highlights')['departments'].find({'priority': {'$exists': False}}))

godown_map = [
    'Department',
    'Category',
    'Sub_category',
    'Sub_category_1',
    'Sub_category_2',
    'Sub_category_3',
    'Sub_category_4',
    'Sub_category_5',
    'Sub_category_6',
    'Sub_category_-',
]


def startBSR(deps, visible, status):
    exist_bsrs = db_mongo.db('scrap_process')['tasks_bodies'].find({'script': 'bsr'})
    exist_bsr_urls = set()
    for bsr in exist_bsrs:
        exist_bsr_urls.add(bsr['data']['bsr'])

    headers = {}
    bodies = {}
    for dep in deps:
        if 'URL' not in dep:
            continue
        url = dep['URL']
        if url in exist_bsr_urls:
            print('Already exists:', url)
            continue
        last_level = dep[godown_map[0]]
        for level in godown_map:
            if dep[level] == 'NaN':
                break
            last_level = dep[level]
        # last_url устанавливает alias & category_name
        # параметров client и target не будет
        # URL будет указано url
        now = datetime.datetime.now(pytz.UTC)
        headers[last_level] = {
            'script': 'bsr',
            'visible': visible,
            'created_at': now,
            'started_at': None,
            'ended_at': None,
            'alias': last_level,
        }
        bodies[last_level] = {
            'script': 'bsr',
            'header_id': None,
            'data': {
                'bsr': url,
                'domain': 'amazon.com',
                'limit': False,
                'unique_brands': False,
                'target': None,
                'category': last_level,
                'client': None,
            },
            'status': status,
            'confirmed_status': status,
            'stage': 1,
            'errors': {},
            'created_at': now,
            'started_at': None,
            'ended_at': None,
            'result': {},
        }
    c = 0
    for bsr_name, data in headers.items():
        c += 1
        res = db_mongo.db('scrap_process')['tasks_headers'].insert_one(data)
        if res.inserted_id:
            bodies[bsr_name]['header_id'] = res.inserted_id
            db_mongo.db('scrap_process')['tasks_bodies'].insert_one(bodies[bsr_name])
        print(c)
        # bodies[bsr_name]['header_id'] = res.inserted_id
    # return ([item['header_id'] for item in bodies.values()],
    #         db_mongo.db('scrap_process')['tasks_headers'].insert_many(list(bodies.values())).inserted_ids)


if priority_deps:
    print(startBSR(priority_deps, True, 0))
if usual_deps:
    print(startBSR(usual_deps, True, 0))
