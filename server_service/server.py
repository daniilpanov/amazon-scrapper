import os.path

import fastapi
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import FileResponse
from . import raw_tasks_router, products_router, sellercentral_router, h10router, cmds_router, google_drive_router

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(raw_tasks_router.router)
app.include_router(products_router.router)
app.include_router(sellercentral_router.router)
app.include_router(h10router.router)
app.include_router(cmds_router.router)
app.include_router(google_drive_router.router)


# WEB VERSION
@app.get('/cp', response_class=FileResponse)
async def cp_show():
    return 'web/index.html'


@app.get('/file', response_class=FileResponse)
async def file(filepath: str):
    return filepath


def start_server(host='0.0.0.0', port=8832):
    import uvicorn
    prefix = './'
    if not os.path.exists(prefix + 'certificate.key'):
        prefix = 'server_service/'
    # uvicorn.run(app, host=host, port=port, ssl_keyfile=prefix + 'certificate.key', ssl_certfile=prefix + 'certificate.crt')
    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    start_server()
