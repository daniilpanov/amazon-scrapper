import json
import re

import fastapi
from bs4 import BeautifulSoup
from fastapi import HTTPException, Body
from pymongo.errors import BulkWriteError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse

import amazon_requests
import tasks
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


@app.get('/cp', response_class=FileResponse)
async def cp_show():
    return 'web-client.html'


@app.post('/tasks/add/{script}')
async def add_task_req(script: str, data=Body()):
    data = json.loads(data)
    if data and 'alias' in data:
        alias = data['alias']
        del data['alias']
    else:
        alias = None
    _id = tasks.add_task(script, alias, data)
    return _id


@app.delete('/tasks/delete/{task_id}')
async def delete_task_req(task_id: int):
    tasks.get_task(task_id).ev.set()
    tasks.delete_task(task_id)


@app.get('/tasks/get/{task_id}')
async def get_task_req(task_id: int):
    return tasks.get_task(task_id).to_dict()


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
            'relation_to_category': data['client_name'],
            'relation_to_TOP5': asin in top5_asins,
        } for asin in asins])
        return fastapi.Response(status_code=fastapi.status.HTTP_204_NO_CONTENT)
    except BulkWriteError:
        pass
    except Exception as e:
        print(type(e))
        raise HTTPException(status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR) from e


@app.get('/cmd/products/get/{asin}')
async def product_get_cmd(asin):
    try:
        res = db('amazon_data')['product_card'].find_one({'asin': asin})
        return res
    except Exception as e:
        raise HTTPException(status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR) from e


@app.get('/tasks/get')
async def get_tasks_req():
    return list(tasks.get_task(_id).to_dict() for _id in tasks.all_tasks if type(_id) is int)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8830)
