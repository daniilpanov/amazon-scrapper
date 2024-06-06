import enum
import mimetypes
from http.client import HTTPException
from io import BytesIO

import requests
from fastapi import APIRouter
from pydantic import BaseModel
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from starlette.responses import Response
from starlette.status import HTTP_404_NOT_FOUND, HTTP_201_CREATED

import google_drive_helper
from db_mongo import db

router = APIRouter(prefix='/sellercentral')
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
credentials = ServiceAccountCredentials.from_json_keyfile_name('amazon-sellercentral.json', scope)
service = build('drive', 'v3', credentials=credentials)


class MediaTypeEnum(enum.Enum):
    pdf = 'pdf'
    int_video = 'int_video'
    yt = 'yt'


class SellerCentral(BaseModel):
    media_link: str
    media_type: MediaTypeEnum
    course_name: str
    module_name: str
    course_id: str
    module_id: str


@router.post('/add')
async def add_result(data: SellerCentral):
    # files = google_drive_helper.get_files('id, name', f"name contains '{data.course_id}' and name contains '{data.module_id}'")
    _type, encoding = mimetypes.guess_type(data.media_link)
    res = requests.get(data.media_link)
    if not res or res.status_code != 200:
        raise HTTPException(HTTP_404_NOT_FOUND)
    google_drive_helper.load_file(BytesIO(res.content), data.course_id + '---' + data.module_id, _type, serv=service)
    google_drive_helper.delete_duplicate_files(serv=service)
    db('amazon_sellercentral')['pdf' if data.media_type == 'pdf' else 'videos'].replace_one({
        'course_id': data.course_id,
        'module_id': data.module_id,
    }, {
        'couse_id': data.course_id,
        'couse_name': data.course_name,
        'module_id': data.module_id,
        'module_name': data.module_name,
    })
    return Response(status_code=HTTP_201_CREATED)
