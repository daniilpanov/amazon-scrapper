import enum
from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import Response
from starlette.status import HTTP_404_NOT_FOUND, HTTP_201_CREATED

import google_drive_helper
import tasks_manager
from db_mongo import db

router = APIRouter(prefix='/sellercentral')


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
    if data.media_type in (MediaTypeEnum.int_video, MediaTypeEnum.yt):
        mimetype = 'video/mp4'
        ext = 'mp4'
    else:
        mimetype = 'application/pdf'
        ext = 'pdf'
    tasks_manager.add_task('gdrive', {
        'alias': 'GDrive: ' + data.course_id + ', ' + data.module_id,
    }, [{
        'filename': data.course_id + '---' + data.module_id + '.' + ext,
        'mimetype': mimetype,
        'media_type': 'yt' if data.media_type == MediaTypeEnum.yt else ('zipvid' if data.media_type == MediaTypeEnum.int_video else 'doc'),
        'media_url': data.media_link,
        'order': 'asc',
        'order_by': 'resolution',
        'first': True,
        'filter': {'progressive': True},
        'service': 'sellercentral',
    }])
    print(google_drive_helper.get_files('id, name', serv='sellercentral'))
    db('amazon_sellercentral')['pdf' if data.media_type == 'pdf' else 'videos'].replace_one({
        'course_id': data.course_id,
        'module_id': data.module_id,
    }, {
        'course_id': data.course_id,
        'course_name': data.course_name,
        'module_id': data.module_id,
        'module_name': data.module_name,
    }, upsert=True)
    return Response(status_code=HTTP_201_CREATED)
