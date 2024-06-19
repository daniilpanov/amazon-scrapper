import importlib
import os

import fastapi
from starlette.middleware.cors import CORSMiddleware

app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

modules = []

if os.path.isdir('server_service'):
    prefix = 'server_service/'
else:
    prefix = './'

for router in os.listdir(prefix):
    if not router.endswith('router.py'):
        continue
    router = router[:-3]
    modules.append(router)
    try:
        module = importlib.import_module('.' + router)
    except (ImportError, TypeError):
        module = importlib.import_module(router)
    try:
        app.include_router(module.router)
    except AttributeError:
        print('Skip router', router)


@app.get('/ping')
async def ping():
    return {'count': len(modules), 'modules': modules}


def run(host='0.0.0.0', port=8832):
    import uvicorn

    # uvicorn.run(app, host=host, port=port, ssl_keyfile=prefix + 'certificate.key', ssl_certfile=prefix + 'certificate.crt')
    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    run()
