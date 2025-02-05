import os

import fastapi
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import ORJSONResponse, RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
import logging

from .settings import WEB_PORT

# Create a logger object
logger = logging.getLogger(__name__)
# Set the logging level to INFO
logger.setLevel(logging.DEBUG)
# Create a handler that logs to the Docker logs
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(handler)

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    for h in request.headers:
        if h.lower() == 'content-type':
            print(await request.json())
            break
    else:
        print(await request.body())
    return ORJSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


modules = []

if os.path.isdir('app'):
    prefix = 'app/'
else:
    prefix = './'

for router in os.listdir(prefix):
    if not router.endswith('router.py'):
        continue
    router = router[:-3]
    try:
        module = __import__(router, globals(), locals(), [], 1)
        try:
            app.include_router(module.router)
            logger.info('Module loaded: ' + router)
            modules.append(router)
        except AttributeError:
            logger.warning('Skip router', router)
    except (ImportError, TypeError) as e:
        logger.warning(e)


@app.get('/ping')
async def ping():
    return {'count': len(modules), 'modules': modules}


@app.get('/cp')
async def redirect_cp(req: Request):
    return RedirectResponse(url=req.url.scheme + '://' + req.url.hostname + ':' + str(WEB_PORT))
