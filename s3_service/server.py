import os.path

import uvicorn
from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.status import HTTP_404_NOT_FOUND

from s3helper import *
from config import PORT

app = FastAPI()


@app.middleware("http")
async def get_file(request: Request, call_next):
    if request.url.path.startswith('/getfile/'):
        res = load_content(request.url.path[9:])
        if not res:
            return Response(status_code=HTTP_404_NOT_FOUND)
        res.seek(0)
        media_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'txt': 'text/plain',
            'html': 'text/html',
            'mp4': 'video/mp4',
            'ts': 'video/mp2t',
        }
        return Response(res.read(), media_type=media_map.get(request.url.path.rsplit('.', maxsplit=1)[-1].lower()))
    elif request.url.path.startswith('/download/'):
        res = load_content(request.url.path[10:])
        if not res:
            return Response(status_code=HTTP_404_NOT_FOUND)
        res.seek(0)
        media_map = {
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'txt': 'text/plain',
            'html': 'text/html',
            'mp4': 'video/mp4',
            'ts': 'video/mp2t',
        }
        resp = Response(res.read(), media_type=media_map.get(request.url.path.rsplit('.', maxsplit=1)[-1].lower()))
        resp.headers.append('Content-Disposition', 'attachment; filename="' + request.url.path.rsplit('/', maxsplit=1)[-1] + '"')
        return resp
    elif request.url.path.startswith('/getlist/'):
        res = [item.key for item in get_file_list(request.url.path[9:])]
        if not res:
            return Response(status_code=HTTP_404_NOT_FOUND)
        return JSONResponse(res)
    return await call_next(request)


if __name__ == '__main__':
    if os.path.isdir('../cert'):
        uvicorn.run(app, host='0.0.0.0', port=PORT, ssl_keyfile='../cert/key.pem', ssl_certfile='../cert/cert.pem')
    else:
        uvicorn.run(app, host='0.0.0.0', port=PORT)
