from hashlib import sha256

from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_403_FORBIDDEN, HTTP_201_CREATED, HTTP_500_INTERNAL_SERVER_ERROR, HTTP_204_NO_CONTENT

from .db_controller import *
from .config import db_config, API_KEY_HASH

dbc = DBController(db_config)
app = FastAPI()


@app.middleware('http')
async def check_auth(request: Request, call_next):
    auth_string = request.headers.get('Authorization')
    if not auth_string or sha256(auth_string.encode('utf-8')) != API_KEY_HASH:
        raise HTTPException(HTTP_403_FORBIDDEN)
    return await call_next(request)


def return_result(res):
    if res:
        return Response({'_id': str(res)}, HTTP_201_CREATED)
    elif res is None:
        return Response(status_code=HTTP_204_NO_CONTENT)
    raise HTTPException(HTTP_500_INTERNAL_SERVER_ERROR)


@app.post('/load/shop')
def load_shop(shop_data: Shop):
    res = dbc.add_shop(shop_data)
    return return_result(res)


@app.post('/load/product')
def load_product(product_data: Product):
    res = dbc.add_product(product_data)
    return return_result(res)


@app.post('/load/creator')
def load_creator(creator_data: Creator):
    res = dbc.add_creator(creator_data)
    return return_result(res)


@app.post('/load/video')
def load_video(video_data: Video):
    res = dbc.add_video(video_data)
    return return_result(res)
