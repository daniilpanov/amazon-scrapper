import os.path

import fastapi
from fastapi import HTTPException
from starlette.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from starlette.responses import Response
from starlette.status import HTTP_200_OK, HTTP_500_INTERNAL_SERVER_ERROR

from solve_captcha_with_model import CaptchaSolver

capsolver = None
if os.path.isdir('app'):
    try:
        capsolver = CaptchaSolver('app')
    except:
        pass
if not capsolver:
    capsolver = CaptchaSolver(os.path.join('captcha_service', 'app'))
app = fastapi.FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


class SolveURLRequest(BaseModel):
    url: str


@app.post('/solve/url')
async def solve_url(request: SolveURLRequest):
    res = capsolver.solve_from_url(request.url)
    if res:
        return Response(status_code=HTTP_200_OK, content=res)
    raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR)


def run(host='0.0.0.0', port=8090):
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == '__main__':
    run(port=int(os.environ.get('DATA_IMPORTER_PORT') or 8090))
