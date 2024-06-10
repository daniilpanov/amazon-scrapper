import datetime

from fastapi import APIRouter, HTTPException
from helpers import orjson_response
from pydantic import BaseModel
from pymongo.errors import PyMongoError, BulkWriteError
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_204_NO_CONTENT

import tasks_manager
from db_mongo import db

router = APIRouter(prefix='/products')


class AmazonTaskConfig(BaseModel):
    alias: str | None = None
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
    collect_reviews: bool = True


@router.post('/collect')
async def collect_products_task(config: AsinsCollectingConfig):
    default_row = {
        'current_format': config.current_format,
        'collect_aspects': config.collect_aspects,
        'collect_media_config': config.collect_media_config,
        'domain': config.domain,
    }
    data = []
    for item in config.asins:
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
    return orjson_response(tasks_manager.add_task('products', {
        'alias': config.alias,
    }, data, stage=int(config.collect_reviews)))


@router.post('/set_result/reviews')
async def set_reviews_result(request: Request):
    data = await request.json()
    if 'scrap_datetime' in data:
        data['scrap_datetime'] = datetime.datetime.fromisoformat(data['scrap_datetime'])
    if 'date' in data:
        data['date'] = datetime.datetime.fromisoformat(data['date'])
    try:
        db('amazon_data')['customer_reviews'].insert_many(data, ordered=False)
    except BulkWriteError:
        pass
    except PyMongoError as e:
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.post('/set_result/card/{asin}')
async def set_product_result(request: Request, asin: str):
    data = await request.json()
    if 'parse_datetime' in data:
        data['parse_datetime'] = datetime.datetime.fromisoformat(data['parse_datetime'])
    try:
        db('amazon_data')['product_card'].replace_one({'asin': asin}, data, upsert=True)
    except PyMongoError as e:
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.post('/set_result/aspects/{asin}')
async def set_aspects_result(request: Request, asin: str):
    data = await request.json()
    return
    try:
        db('amazon_data')['aspects'].replace_one({'asin': asin}, data, upsert=True)
    except PyMongoError as e:
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e
    return Response(status_code=HTTP_204_NO_CONTENT)
