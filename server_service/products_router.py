import datetime

from fastapi import APIRouter, HTTPException

import parser
from helpers import orjson_response
from pydantic import BaseModel, field_validator
from pymongo.errors import PyMongoError, BulkWriteError
from starlette.responses import Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_404_NOT_FOUND, \
    HTTP_400_BAD_REQUEST

import tasks_manager
from db_mongo import db

router = APIRouter(prefix='/products')
AMADATA = db('amazon_data')


def _cast_iso_dt_to_dt_obj(dt: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(dt)


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


class AspectsResultItem(BaseModel):
    Aspect: str
    positive: int
    negative: int

    def compare_with_asin(self, asin, **kwargs):
        kwargs['mode'] = 'python'  # json strings incompatible with python dicts
        return super().model_dump(**kwargs) | {'ASIN': asin}


class ProductsResultItem(BaseModel):
    asin: str
    product_url: str
    canonical_link: str
    product_title: str
    product_descr: str
    picture_url: str
    parse_datetime: datetime.datetime
    features: dict[str, str] | None
    top_5_phrases: list[str] | None
    product_price: int | None

    _cast_parse_datetime = field_validator('parse_datetime', mode='before')(_cast_iso_dt_to_dt_obj)


class ReviewsResultItem(BaseModel):
    asin: str
    review_id: str
    product_url: str
    date: datetime.datetime
    country: str
    name: str
    title: str
    description: str
    rating: int = 0
    helpful: int = 0
    options: str | None
    scrap_datetime: datetime.datetime

    _cast_scrap_datetime = field_validator('scrap_datetime', mode='before')(_cast_iso_dt_to_dt_obj)
    _cast_date = field_validator('date', mode='before')(_cast_iso_dt_to_dt_obj)


@router.post('/collect')
async def collect_products_task(config: AsinsCollectingConfig):
    default_row = {
        'current_format': config.current_format,
        'collect_aspects': config.collect_aspects,
        'collect_media_config': config.collect_media_config,
        'target': config.collect_media_config,
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
async def set_reviews_result(reviews: list[ReviewsResultItem]):
    try:
        AMADATA['customer_reviews'].insert_many([model.model_dump() for model in reviews], ordered=False)
    except BulkWriteError:
        pass
    except PyMongoError as e:
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.post('/set_result/card/{asin}')
async def set_product_result(asin: str, card: ProductsResultItem):
    try:
        AMADATA['product_card'].replace_one({'asin': asin}, card.model_dump(), upsert=True)
    except PyMongoError as e:
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.post('/set_result/aspects/{asin}')
async def set_aspects_result(asin: str, aspects: list[AspectsResultItem]):
    try:
        replace_aspects = []
        data = []
        for aspect in aspects:
            replace_aspects.append(aspect.Aspect)
            data.append(aspect.to_dict(asin))
        print(replace_aspects)
        print(data)
        AMADATA['aspects'].delete_many({'ASIN': asin, 'Aspect': {'$in': replace_aspects}})
        AMADATA['aspects'].insert_many(data, ordered=False)
    except BulkWriteError:
        pass
    except PyMongoError as e:
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e
    return Response(status_code=HTTP_201_CREATED)


@router.post('/target/collect/{asin}')
async def collect_product_media(asin: str):
    product_card = AMADATA['product_card'].find_one({'asin': asin})
    if not product_card:
        raise HTTPException(HTTP_404_NOT_FOUND)
    if not (media_data := product_card.get('media_data')):
        raise HTTPException(HTTP_400_BAD_REQUEST)
    images, videos = parser.get_media_links(asin, media_data)

    def add_task(i, link, mimetype, ext):
        fname = asin + '-' + str(i + 1)
        tasks_manager.add_task('gdrive', {
            'alias': 'GDrive: ' + fname,
        }, [{
            'filename': fname,
            'mimetype': mimetype,
            'media_type': ext,
            'media_url': link,
            'service': 'sellercentral',
        }])

    for i, image_url in enumerate(images):
        add_task(i, image_url, 'image/jpeg', 'jpg')

    for i, video_url in enumerate(videos):
        add_task(i, video_url, 'video/mp4', 'mp4')

