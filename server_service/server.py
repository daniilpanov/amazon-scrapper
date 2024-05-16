import json
import os.path
import re
from collections import defaultdict
from json import JSONDecodeError

import fastapi
import pandas as pd
from bs4 import BeautifulSoup
from bson import json_util, ObjectId
from fastapi import HTTPException, Body, Request
from pydantic import BaseModel
from pymongo.errors import BulkWriteError, PyMongoError
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.responses import FileResponse, JSONResponse
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT, HTTP_500_INTERNAL_SERVER_ERROR

import amazon_requests
import tasks_manager
import tasks_manager as tasks
from database import db
from helpers import get_all_asins_from_text

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)
# app.add_middleware(GZipMiddleware)


# ANNOTATIONS
class TaskConfig(BaseModel):
    alias: str | None = None


class AmazonTaskConfig(TaskConfig):
    domain: str = 'amazon.com'


class AsinsItemCollectConfig(BaseModel):
    asin: str
    keywords: list[str] | None = None
    collect_aspects: bool | None = None
    current_format: bool | None = None
    collect_media_config: bool | None = None


class AsinsCollectingConfig(AmazonTaskConfig):
    asins: list[AsinsItemCollectConfig]
    collect_aspects: bool = True
    current_format: bool = True
    collect_media_config: bool = False


# WEB VERSION
@app.get('/cp', response_class=FileResponse)
async def cp_show():
    return 'web/index.html'


# USUAL ENDPOINTS
@app.post('/products/collect')
async def collect_products_task(config: AsinsItemCollectConfig):
    default_row = {
        'current_format': config.current_format,
        'collect_aspects': config.collect_aspects,
        'collect_media_config': config.collect_media_config,
    }
    data = []
    for item in config.asins:
        item: AsinsItemCollectConfig
        if item.keywords:
            for keyword in item.keywords:
                row = default_row.copy()
                row['asin'] = item.asin
                row['keywords'] = keyword
                data.append(row)
        else:
            row = default_row.copy()
            row['asin'] = item.asin
            row['keywords'] = ''
            data.append(row)
    tasks_manager.add_task('reviews', {
        'alias': config.alias,
    }, data)


class HeliumTask(TaskConfig):
    asins: tuple[str, ...]


@app.post('/helium/get')
async def get_helium(config: HeliumTask):
    data = json.loads(json_util.dumps(
        tasks.add_task('h10', {'alias': config.alias or ','.join(config.asins) + '#h10'}, [{'asins': config.asins}]),
    ))
    return data[0]['$oid'] + '--' + data[1][0]['$oid']


@app.get('/helium/result/{helium_id}')
async def get_helium_result(helium_id: str):
    if '--' not in helium_id:
        raise HTTPException(HTTP_400_BAD_REQUEST)
    header_id, body_id = helium_id.split('--')
    task = tasks.get_task(body_id, True)
    if not task or task['status'] == tasks.TaskStatusEnum.stopped:
        raise HTTPException(HTTP_404_NOT_FOUND)
    if task['status'] < tasks.TaskStatusEnum.finished:
        return None
    return task['result']


@app.post('/helium/set/{helium_id}')
async def set_helium_result(request: Request, helium_id: str):
    request_data = {}
    try:
        request_data = await request.json()
    except JSONDecodeError:
        pass
    if 'export' not in request_data or 'titles' not in request_data:
        print('no needle data!')
        raise HTTPException(HTTP_400_BAD_REQUEST)
    print(request_data['export'][:100])
    try:
        data = pd.read_csv(request_data['export'], index_col=None)
    except ValueError as e:
        print(e)
        raise HTTPException(HTTP_400_BAD_REQUEST)
    csv = data.to_csv(index=False)
    try:
        res = tasks.TasksBodies.update_one({'_id': ObjectId(helium_id)}, {'$set': {'result': {
            'titles': request_data['titles'], 'csv_data': csv,
        }}}).modified_count
    except PyMongoError as e:
        print(e)
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR)
    tasks.finish_task(helium_id, True)
    tasks.release_task(helium_id)
    return res


@app.delete('/tasks/delete/{header_id}')
async def delete_task_req(header_id: str, force_delete: bool = False):
    return tasks.remove_task(header_id, force_delete)


@app.patch('/tasks/confirm/{task_id}')
async def confirm_task_status_req(task_id: str, confirm_status: int):
    return tasks.confirm_status(task_id, confirm_status)


@app.patch('/tasks/stop/{task_id}')
async def stop_task_req(task_id: str):
    return tasks.stop_task(task_id)


@app.patch('/tasks/finish/{task_id}')
async def finish_task_req(task_id: str, confirm: bool = True):
    return tasks.finish_task(task_id, confirm)


@app.get('/tasks/get/{task_id}')
async def get_task_req(task_id: str, with_header: bool = True, body_only: bool = False):
    data = tasks.get_task(task_id, with_header)
    if body_only:
        data = data['result']
    return JSONResponse(json.loads(json_util.dumps(data)))


@app.get('/tasks/get')
@app.get('/tasks/get/{script}')
async def get_tasks_req(script: str | None = None):
    res = list(tasks.get_all_tasks({'script': script} if script else None))
    return JSONResponse(json.loads(json_util.dumps(res)))


@app.get('/tasks/filter')
async def filter_tasks_req(_filter: str):
    prepared_filter = json.loads(_filter)
    return JSONResponse(json.loads(json_util.dumps(tasks.get_all_tasks(prepared_filter))))


@app.post('/tasks/acquire/{script}/{header_id}/{task_id}')
async def acquire_task_req(script: str, header_id: str, task_id: str):
    res = tasks.acquire_task(script, task_id, header_id)
    if not res:
        raise HTTPException(HTTP_409_CONFLICT)
    if res:
        tasks.set_status(task_id, tasks.TaskStatusEnum.started, True)
    return JSONResponse(json.loads(json_util.dumps(res)))


@app.post('/tasks/release/{task_id}')
async def release_task_req(task_id: str):
    return tasks.release_task(task_id)


@app.get('/tasks/get_available')
@app.get('/tasks/get_available/{script}')
async def get_available_tasks_req(script: str | None = None):
    res = list(tasks.get_all_tasks(
        ({'script': script} if script else {}) | {'status': {'$lt': tasks.TaskStatusEnum.stopped},
                                                  'taskLock': {'$exists': False}}))
    return JSONResponse(json.loads(json_util.dumps(res)))


@app.get('/file', response_class=FileResponse)
async def file(filepath: str):
    return filepath


# SPECIAL ENDPOINTS
@app.get('/cmd/reviews/count')
async def reviews_count_cmd(asin: str, current_format: bool = True):
    try:
        count = db('amazon_data')['customer_reviews'].count_documents({'asin': asin})
        sess = amazon_requests.Requests()
        await sess.init()
        soup = BeautifulSoup(await sess.get_reviews(asin, params={
            'formatType': 'current_format' if current_format else '',
        }, xmlhttp=False), features='lxml')
        reviews_count_element = soup.select_one('[data-hook="cr-filter-info-review-rating-count"]')
        while not reviews_count_element:
            await sess.init()
            soup = BeautifulSoup(await sess.get_reviews(asin, params={
                'formatType': 'current_format' if current_format else '',
            }, xmlhttp=False), features='lxml')
            reviews_count_element = soup.select_one('[data-hook="cr-filter-info-review-rating-count"]')

        reviews_count = 0
        reviews_count_part = ''.join(re.findall(r'[0-9., ]+', reviews_count_element.text)).split(' ,')
        if len(reviews_count_part) == 2:
            reviews_count = int(float(reviews_count_part[1].replace(',', '').replace(' ', '')))
        return count, reviews_count, asin
    except Exception as e:
        raise HTTPException(status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR) from e


@app.post('/cmd/category/set')
async def category_set_cmd(data=Body()):
    data = json.loads(data)
    asins = data['asins']
    if type(asins) is str:
        asins = get_all_asins_from_text(asins)
    top5_asins = set(data['top5_asins'])
    try:
        db('amazon_data')['all_categories'].insert_many([{
            'Category': data['cat_name'],
            'ASIN': asin,
            'relation_to_category': data['client_name'] if asin == data.get('target') else None,
            'relation_to_TOP5': asin in top5_asins,
        } for asin in asins])
        return fastapi.Response(status_code=fastapi.status.HTTP_201_CREATED)
    except BulkWriteError:
        pass
    except Exception as e:
        print(type(e), e)
        raise HTTPException(status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR) from e


@app.get('/cmd/products/get/{asin}')
async def product_get_cmd(asin: str):
    try:
        product_card = db('amazon_data')['product_card'].find_one({'asin': asin})
        try:
            aspects = [(i['Aspect'], i['positive'], i['negative']) for i in db('amazon_data')['amazon_aspects'].find({
                'ASIN': asin,
            })]
        except:
            aspects = None
        try:
            category = db('amazon_data')['all_categories'].find_one({'ASIN': asin}) or defaultdict(lambda: None)
        except:
            category = defaultdict(lambda: None)
        if not product_card:
            raise HTTPException(status_code=fastapi.status.HTTP_404_NOT_FOUND)
        return {
            'ASIN': asin,
            'URL': product_card['product_url'],
            'Title': product_card['product_title'],
            'Description': product_card['product_descr'],
            'Features': product_card['features'],
            'Top 5 phrases': product_card['top_5_phrases'],
            'Price': product_card['product_price'],
            'Aspects': aspects,
            'Category': [category['Category'], category['relation_to_category']],
            'Picture': product_card['picture_url'],
        }
    except Exception as e:
        raise HTTPException(status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR) from e


def start_server(host='0.0.0.0', port=8832):
    import uvicorn
    prefix = './'
    if not os.path.exists(prefix + 'certificate.key'):
        prefix = 'server_service/'
    # uvicorn.run(app, host=host, port=port, ssl_keyfile=prefix + 'certificate.key', ssl_certfile=prefix + 'certificate.crt')
    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    start_server()
