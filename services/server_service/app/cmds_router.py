from collections import defaultdict

import orjson
import pymongo
from fastapi import APIRouter, Body
from pydantic import BaseModel
from pymongo.errors import BulkWriteError, PyMongoError
from starlette.exceptions import HTTPException
from starlette.responses import Response
from starlette.status import HTTP_404_NOT_FOUND, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_201_CREATED

from . import helpers
from . import tasks_manager
from .db_mongo import db
from .helpers import get_all_asins_from_text
from . import products_router

router = APIRouter(prefix='/cmd')


class CollectProductsForm(BaseModel):
    alias: str | None = None
    category_name: str | None = None
    client_name: str | None = None
    asins: str | list[str]
    target: str | None = None
    collect_aspects: bool = False
    collect_reviews: bool = False
    current_format: bool = False


@router.post('/alias/products/collect')
async def collect_products_form(config: CollectProductsForm):
    asins = config.asins or []
    target = config.target or []
    if isinstance(asins, str):
        asins = get_all_asins_from_text(asins)
    if isinstance(target, str):
        target = get_all_asins_from_text(target)
    asins += target
    if config.category_name:
        await category_set_cmd({
            'asins': asins,
            'top5_asins': [],
            'target': target or None,
            'cat_name': config.category_name,
            'client_name': config.client_name,
        })
    target = set(target)
    asins = list(set(asins))
    res = await products_router.collect_products_task(products_router.AsinsCollectingConfig(**{
        'alias': config.alias,
        'asins': [products_router.AsinsItemCollectConfig(
            asin=asin,
            collect_media_config=asin in target,  # if asin=target then collect media
        ) for asin in asins],
        'collect_aspects': config.collect_aspects,
        'collect_reviews': config.collect_reviews,
        'current_format': config.current_format,
    }))
    return res


class BSRCollectingConfig(BaseModel):
    alias: str | None = None
    category: str | None = None
    client: str | None = None
    bsr: str
    count: int = 30
    target: str | None = None
    with_continue: bool = False
    domain: str = 'amazon.com'


class BSRResult(BaseModel):
    task_id: str
    with_continue: bool = False
    asins: list
    currentBSR: dict[str, str | int]
    tree: list | None = None


class BSRTreeResultItem(BaseModel):
    asin: str
    title: str
    score: float | None = None
    number_in_BSR: int
    image: str | None = None


class BSRTreeResult(BaseModel):
    task_id: str
    bsr_link: str
    items: list[BSRTreeResultItem]


@router.post('/alias/bsr/collect')
async def collect_bsr_cmd(config: BSRCollectingConfig):
    data = {'bsr': config.bsr, 'target': config.target, 'count': config.count,
            'category': config.category, 'client': config.client, 'domain': config.domain}
    return helpers.orjson_response(tasks_manager.add_task('bsr', {
        'alias': config.alias,
    }, [data], stage=int(config.with_continue)))


@router.post('/alias/bsr/finish')
async def finish_bsr_cmd(bsr: BSRResult):
    if bsr.with_continue:
        tasks_manager.set_task_stage(bsr.task_id, 2, True, result={
            'bsr': bsr.currentBSR,
            'asins': bsr.asins,
        })
    else:
        tasks_manager.finish_task(bsr.task_id, True, result={
            'bsr': bsr.currentBSR,
            'asins': bsr.asins,
        })
        tasks_manager.release_task(bsr.task_id)
    return Response(status_code=HTTP_201_CREATED)


@router.post('/alias/bsrtree/finish')
async def finish_bsrtree_cmd(bsr: BSRTreeResult):
    result = bsr.model_dump(include={'items'})['items']
    tasks_manager.finish_task(bsr.task_id, True)
    db('ai_highlights')['departments'].update_one({'URL': bsr.bsr_link, 'items': {'$exists': False}},
                                                  {'$set': {'items': result}})
    tasks_manager.release_task(bsr.task_id)
    return Response(status_code=HTTP_201_CREATED)


@router.post('/category/set')
async def category_set_cmd(data=Body()):
    if not isinstance(data, (dict, list, tuple)):
        data = orjson.loads(data)
    asins = data['asins']
    if isinstance(asins, str):
        asins = get_all_asins_from_text(asins)
    target = data.get('target', [])
    if isinstance(target, str):
        target = get_all_asins_from_text(target)
    top5_asins = set(data.get('top5_asins', []))
    client_name = data.get('client_name')
    try:
        operations = [
            pymongo.UpdateOne(
                {'Category': data['cat_name'], 'ASIN': asin},  # Фильтр для поиска существующих записей
                {
                    '$set': {
                        'relation_to_category': client_name if asin in target else None,
                        'relation_to_TOP5': asin in top5_asins,
                    }
                },
                upsert=True,
            )
            for asin in asins
        ]
        if operations:
            db('amazon_data')['all_categories'].bulk_write(operations)
        # db('amazon_data')['all_categories'].insert_many([{
        #     'Category': data['cat_name'],
        #     'ASIN': asin,
        #     'relation_to_category': client_name if asin in target else None,
        #     'relation_to_TOP5': asin in top5_asins,
        # } for asin in asins])
        return Response(status_code=HTTP_201_CREATED)
    except BulkWriteError:
        pass
    except Exception as e:
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
