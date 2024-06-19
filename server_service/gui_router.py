from fastapi import APIRouter
from starlette.responses import FileResponse

router = APIRouter()


@router.get('/cp', response_class=FileResponse)
async def cp_show():
    return 'web/index.html'


@router.get('/file', response_class=FileResponse)
async def file(filepath: str):
    return filepath
