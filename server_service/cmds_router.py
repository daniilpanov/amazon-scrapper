import asyncio
import re
from collections import defaultdict

import fastapi
import orjson
import requests
from bs4 import BeautifulSoup
from fastapi import APIRouter, Body
from pydantic import BaseModel
from pymongo.errors import BulkWriteError, PyMongoError
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_201_CREATED, \
    HTTP_503_SERVICE_UNAVAILABLE

import helpers
import tasks_manager
from db_mongo import db
from helpers import get_all_asins_from_text
from . import products_router

router = APIRouter(prefix='/cmd')


class CollectProductsForm(BaseModel):
    alias: str | None = None
    category_name: str | None = None
    client_name: str | None = None
    asins: str
    target: str | None = None
    collect_aspects: bool = False
    collect_reviews: bool = False
    current_format: bool = False
    top5: bool = False


@router.post('/alias/products/collect')
async def collect_products_form(config: CollectProductsForm):
    asins = get_all_asins_from_text(config.asins) + ([config.target] if config.target else [])
    print(config.target)
    print(asins[0])
    print(asins[0] == config.target)
    if config.category_name:
        await category_set_cmd({
            'asins': asins,
            'top5_asins': asins[:5] if config.top5 else [],
            'target': config.target or None,
            'cat_name': config.category_name,
            'client_name': config.client_name,
        })
    res = await products_router.collect_products_task(products_router.AsinsCollectingConfig(**{
        'alias': config.alias,
        'asins': [products_router.AsinsItemCollectConfig(
            asin=asin,
            collect_media_config=asin == config.target,  # if asin=target then collect media
        ) for asin in asins],
        'collect_aspects': config.collect_aspects,
        'collect_reviews': config.collect_reviews,
        'current_format': config.current_format,
    }))
    return res


class BSRCollectingConfig(BaseModel):
    alias: str | None = None
    domain: str = 'amazon.com'
    category: str | None = None
    client: str | None = None
    bsr: str
    limit: bool = True
    unique_brands: bool = False
    count: int = 30
    target: str | None = None
    with_continue: bool = False


class BSRResult(BaseModel):
    task: BSRCollectingConfig
    bsr_url: str
    asins_links: dict[str, str]


@router.post('/alias/bsr/collect')
async def collect_bsr_cmd(config: BSRCollectingConfig):
    data = {'bsr': config.bsr}
    data['domain'] = config.domain
    data['limit'] = config.limit
    data['unique_brands'] = config.unique_brands
    data['target'] = config.target
    data['count'] = config.count
    data['category'] = config.category
    data['client'] = config.client
    data['with_continue'] = config.with_continue
    return helpers.orjson_response(tasks_manager.add_task('bsr', {
        'alias': config.alias,
    }, [data]))


@router.post('/alias/bsr/finish')
async def set_reviews_result(bsr: BSRResult):
    tasks_manager.finish_task(bsr.task._id, True, result={'url': bsr.bsr_url, 'asins_links': bsr.asins_links})
    tasks_manager.release_task(bsr.task._id)
    asins = list(bsr.asins_links.keys())
    if bsr.task.category:
        await category_set_cmd({
            'asins': asins,
            'top5_asins': asins[:5],
            'target': bsr.task.target or None,
            'cat_name': bsr.task.category,
            'client_name': bsr.task.client,
        })
    if bsr.task.with_continue:
        return await collect_products_form(CollectProductsForm(
            alias=bsr.task.alias,
            asins=asins,
            target=bsr.task.target,
            collect_aspects=True,
            collect_reviews=True,
            current_format=True,
        ))
    return Response(status_code=HTTP_201_CREATED)


@router.get('/reviews/count')
async def reviews_count_cmd(asin: str, current_format: bool = True):
    try:
        cookie = db('amazon_data')['__cookies'].find_one(
            {'session-id': {'$exists': True}, 'sp-cdn': {'$exists': False}})
        count = db('amazon_data')['customer_reviews'].count_documents({'asin': asin})
        data = db('amazon_data')['product_card'].find_one({'asin': asin})
        soup = None
        for i in range(30):
            res = requests.get(
                (data.get('canonical_link',
                          'https://www.amazon.com/product-reviews/' + asin + '/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews') + '&formatType=' + (
                     'current_format' if current_format else '')),
                cookies=cookie,
                headers=helpers.get_request_headers(),
            )
            if res.status_code and res.text:
                html = res.text
                soup = BeautifulSoup(html, features='lxml')
                reviews_count_element = soup.select_one('[data-hook="cr-filter-info-review-rating-count"]')
                if reviews_count_element:
                    break
            await asyncio.sleep(1)
        if not soup:
            raise HTTPException(HTTP_503_SERVICE_UNAVAILABLE)
        reviews_count_element = soup.select_one('[data-hook="cr-filter-info-review-rating-count"]')
        reviews_count = 0
        reviews_count_part = ''.join(re.findall(r'[0-9., ]+', reviews_count_element.text)).split(' ,')
        if len(reviews_count_part) == 2:
            reviews_count = int(float(reviews_count_part[1].replace(',', '').replace(' ', '')))
        return count, reviews_count, asin
    except Exception as e:
        raise HTTPException(status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR) from e


@router.post('/category/set')
async def category_set_cmd(data=Body()):
    if not isinstance(data, (dict, list, tuple)):
        data = orjson.loads(data)
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
        return Response(status_code=HTTP_201_CREATED)
    except BulkWriteError:
        pass
    except Exception as e:
        print(type(e), e)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR) from e


@router.get('/products/get/{asin}')
async def product_get_cmd(asin: str):
    try:
        if not (product_card := db('amazon_data')['product_card'].find_one({'asin': asin})):
            raise HTTPException(status_code=HTTP_404_NOT_FOUND)
        try:
            aspects = [(i['Aspect'], i['positive'], i['negative']) for i in db('amazon_data')['amazon_aspects'].find({
                'ASIN': asin,
            })]
        except PyMongoError as e:
            print('[Warning]', type(e), e)
            aspects = None
        try:
            category = db('amazon_data')['all_categories'].find_one({'ASIN': asin}) or defaultdict(lambda: None)
        except PyMongoError as e:
            print('[Warning]', type(e), e)
            category = defaultdict(lambda: None)
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
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR) from e
