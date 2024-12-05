import datetime
import typing

import pytz
from bson import ObjectId
from fastapi import APIRouter, HTTPException

from .helpers import orjson_response
from pydantic import BaseModel, field_validator
from pymongo.errors import PyMongoError, BulkWriteError
from starlette.responses import Response
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR, HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_404_NOT_FOUND, \
    HTTP_400_BAD_REQUEST

from . import tasks_manager
from .db_mongo import db

router = APIRouter(prefix='/products')
AMADATA = db('amazon_data')
AMAREPS = db('amazon_reports_dev')


def _cast_iso_dt_to_dt_obj(dt: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(dt)


class AmazonTaskConfig(BaseModel):
    alias: str | None = None
    domain: str = 'amazon.com'


class AsinsItemCollectConfig(BaseModel):
    asin: str
    rank: int | None = None
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
    bsr_link: str | None = None


class AspectsResultItem(BaseModel):
    Aspect: str
    positive: int
    negative: int

    def compare_with_asin(self, asin, **kwargs):
        kwargs['mode'] = 'python'  # json strings incompatible with python dicts
        return super().model_dump(**kwargs) | {'ASIN': asin}


class ProductsResultItem(BaseModel):
    rootAsin: str | None = None
    marketplaceId: str | None = None
    asin: str
    title: str | None = None
    breadcrumbs: list[str] | None = None
    currentBreadcrumb: str | None = None
    description: str | None = None
    picture_url: str | None = None
    pictures_urls: list[str | None] | None = None
    price: int | float | None = None
    rating: int | float | None = None
    reviewsCount: int | None = None
    options: dict | None = None
    currentOptions: dict[str, str] | None = None
    relatedProducts: dict | None = None
    relatedVideos: list[str] | None = None
    mediaConfig: dict | list | None = None
    collectMedia: bool = False
    aspects: list[AspectsResultItem] | None = None
    bsr_url: str | None = None
    number_in_BSR: int | None = None


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
    options: typing.Any

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
                if item.current_format is not None:
                    row['current_format'] = item.current_format
                if item.collect_aspects is not None:
                    row['collect_aspects'] = item.collect_aspects
                if item.collect_aspects is not None:
                    row['collect_media_config'] = item.collect_media_config
                    row['target'] = item.collect_media_config
                data.append(row)
        else:
            row = default_row.copy()
            row['asin'] = item.asin
            row['keywords'] = ''
            if item.current_format is not None:
                row['current_format'] = item.current_format
            if item.collect_aspects is not None:
                row['collect_aspects'] = item.collect_aspects
            if item.collect_media_config is not None:
                row['collect_media_config'] = item.collect_media_config
                row['target'] = item.collect_media_config
            data.append(row)
    return orjson_response(tasks_manager.add_task('products', {
        'alias': config.alias,
    }, data, stage=int(config.collect_reviews)))


@router.post('/set_result/reviews')
async def set_reviews_result(reviews: list[ReviewsResultItem]):
    try:
        AMADATA['customer_reviews'].insert_many(
            [model.model_dump() | {'scrap_datetime': datetime.datetime.now(pytz.UTC)} for model in reviews],
            ordered=False,
        )
    except BulkWriteError:
        pass
    except PyMongoError as e:
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR) from e
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.post('/set_result/card/{asin}')
async def set_product_result(asin: str, card: ProductsResultItem):
    if card.bsr_url:
        deps = db('ai_highlights')['departments'].find({'URL': {'$regex': '^/' + card.bsr_url}})
        for dep in deps:
            db('ai_highlights')['departments'].update_one({'_id': dep['_id']}, {'$pull': {'items': {'asin': asin}}})
            db('ai_highlights')['departments'].update_one({'_id': dep['_id']}, {'$push': {'items': {
                'asin': card.asin,
                'title': card.title,
                'score': card.rating,
                'number_in_BSR': card.number_in_BSR,
                'image': card.picture_url,
            }}})

    if card.picture_url:
        main_uri, *_, ext = card.picture_url.rsplit('.', maxsplit=2)
        card.picture_url = main_uri + '.' + ext

    if card.pictures_urls:
        sizing_pictures = []
        urls = card.pictures_urls
        card.pictures_urls = []
        decr = 0
        for i, url in enumerate(urls):
            if not url:
                decr += 1
                continue
            i -= decr
            main_uri, *_, ext = url.rsplit('.', maxsplit=2)
            card.pictures_urls.append(main_uri + '.' + ext)
            variant = 'MAIN' if not i else ('PT' + ('0' if i < 9 else '') + str(i))
            sizing_pictures.append({
                'asin': card.asin,
                'width': 1080, 'height': 1080,
                'marketplace_id': card.marketplaceId,
                'user_id': '99376b43-3a2d-4994-a3cb-e712c1da35d1',
                'variant': variant,
                'link': main_uri + '._SM1080.' + ext,
            })
            sizing_pictures.append({
                'asin': card.asin,
                'width': 550, 'height': 550,
                'marketplace_id': card.marketplaceId,
                'user_id': '99376b43-3a2d-4994-a3cb-e712c1da35d1',
                'variant': variant,
                'link': main_uri + '._SX550.' + ext,
            })
            sizing_pictures.append({
                'asin': card.asin,
                'width': 65, 'height': 65,
                'marketplace_id': card.marketplaceId,
                'user_id': '99376b43-3a2d-4994-a3cb-e712c1da35d1',
                'variant': variant,
                'link': main_uri + '._SX65.' + ext,
            })
        if sizing_pictures:
            try:
                AMAREPS['catalog_images'].insert_many(
                    sizing_pictures,
                    ordered=False,
                )
            except BulkWriteError:
                pass
            except PyMongoError as e:
                raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    data = {
        'asin': card.asin,
        'root_asin': card.rootAsin,
        'product_url': 'https://www.amazon.com/dp/' + card.asin,
        'product_title': card.title,
        'product_descr': card.description,
        'product_price': card.price,
        **card.model_dump(exclude={'asin', 'rootAsin', 'title', 'description', 'price', 'aspects', 'collectMedia'}),
        'parse_datetime': datetime.datetime.now(pytz.UTC)
    }
    try:
        AMADATA['product_card'].replace_one(
            {'asin': {'$in': [asin, card.asin]}},
            data,
            upsert=True,
        )
    except PyMongoError as e:
        raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    replace_aspects = []
    data = []
    if card.aspects:
        for aspect in card.aspects:
            replace_aspects.append(aspect.Aspect)
            data.append(aspect.compare_with_asin(card.asin))
        try:
            AMADATA['aspects'].delete_many({'ASIN': asin, 'Aspect': {'$in': replace_aspects}})
            AMADATA['aspects'].insert_many(data, ordered=False)
        except BulkWriteError:
            pass
        except PyMongoError as e:
            raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e

    if card.collectMedia and card.relatedVideos:
        try:
            tasks_manager.add_task('s3load', {
                'alias': asin + '(' + card.asin + ')' + '#media',
            }, [{
                'videoUrl': url,
                'asin': card.asin,
                'variant': i + 1,
                'prefix': 'products/videos/',
                'filename': card.asin + '_' + url.rsplit('/', maxsplit=2)[1] + '.mp4',
                'mimetype': 'video/mp4',
                'media_type': 'm3u',
            } for i, url in enumerate(card.relatedVideos)])
        except PyMongoError as e:
            raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
    return Response(status_code=HTTP_204_NO_CONTENT)


@router.post('/target/collect/{asin}')
async def collect_product_media(asin: str):
    product_card = AMADATA['product_card'].find_one({'asin': asin})
    if not product_card:
        raise HTTPException(HTTP_404_NOT_FOUND)
    if not (media_data := product_card.get('media_data')):
        raise HTTPException(HTTP_400_BAD_REQUEST)

    def add_task(i, link, mimetype, ext):
        fname = asin + '-' + str(i + 1)
        tasks_manager.add_task('gdrive', {
            'alias': 'GDrive: ' + fname,
        }, [{
            'filename': fname,
            'mimetype': mimetype,
            'media_type': ext,
            'media_url': link,
            'service': 'target',
        }])

    for i, image_url in enumerate(media_data.get('images', [])):
        add_task(i, image_url, 'image/jpeg', 'jpg')

    for i, video_url in enumerate(media_data.get('videos', [])):
        add_task(i, video_url, 'video/mp4', 'mp4')
    return Response(status_code=HTTP_201_CREATED)

