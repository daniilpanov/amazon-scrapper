from fastapi import APIRouter, HTTPException
from fastapi.responses import ORJSONResponse
from starlette.responses import Response
from starlette.status import HTTP_404_NOT_FOUND, HTTP_204_NO_CONTENT

from . import google_drive_helper

router = APIRouter(prefix='/drive')


@router.get('/list')
async def get_files(service: str | None = None):
    return ORJSONResponse(google_drive_helper.get_files(serv=service))


@router.get('/file/{name}')
async def get_file(name: str, service: str | None = None):
    files = google_drive_helper.get_files('id, mimeType', f'name=\'{name}\'', serv=service)
    if not files:
        raise HTTPException(HTTP_404_NOT_FOUND)
    if len(files) > 1:
        google_drive_helper.delete_duplicate_files(service)
    file_bytes = google_drive_helper.download_file(files[0]['id'], serv=service)
    return Response(file_bytes, media_type=files[0]['mimeType'])


@router.delete('/')
@router.delete('/{file_id}')
async def delete_files(file_id: str | None = None, file_name: str | None = None, service: str | None = None):
    drive = google_drive_helper.services.get(service)
    if not drive:
        raise HTTPException(HTTP_404_NOT_FOUND)
    if file_name:
        files = [i['id'] for i in google_drive_helper.get_files('id, name', f'name=\'{file_name}\'', serv=service)]
    else:
        files = [i['id'] for i in google_drive_helper.get_files('id, name', serv=service)]
    if file_id:
        files.append(file_id)
    for file_id in files:
        drive.files().delete(fileId=file_id).execute()
    return Response(status_code=HTTP_204_NO_CONTENT)
